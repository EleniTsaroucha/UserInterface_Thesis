from __future__ import annotations

import hashlib
import random

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from trial_plan import Trial, build_trial_plan

TRIAL_MAX_DURATION_MS = 6 * 60 * 1000
BREAK_AFTER_BLOCK_MS = 5 * 60 * 1000     # §4: 5λεπτο διάλειμμα ανά backend block


class ProtocolRunner(QObject):

    trial_started = pyqtSignal(object)          # Trial
    trial_finished = pyqtSignal(object, bool)   # Trial, completed_naturally
    attacker_window_opened = pyqtSignal(object, int)  # Trial, ms από την έναρξη
    block_break = pyqtSignal(int)               # δείκτης block που μόλις τελείωσε
    session_finished = pyqtSignal()

    def __init__(self, session_id: str, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.trials: list[Trial] = build_trial_plan(session_id)
        self._ptr = 0

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

        self._attacker_timer = QTimer(self)
        self._attacker_timer.setSingleShot(True)
        self._attacker_timer.timeout.connect(self._on_attacker_window)

        rng = random.Random(
            int(hashlib.sha256(f"{session_id}:attacker".encode("utf-8")).hexdigest()[:16], 16)
        )
        self.attacker_offsets_ms = [rng.randint(60_000, 150_000) for _ in self.trials]

    def start(self) -> None:
        self._ptr = 0
        self._enter_trial()

    def stop(self) -> None:
        """Σταματά τους χρονιστές trial και παραθύρου επιτιθέμενου."""
        self._timer.stop()
        self._attacker_timer.stop()

    def current_trial(self) -> Trial | None:
        return self.trials[self._ptr] if self._ptr < len(self.trials) else None

    def notify_action(self, action_id: str) -> None:
        trial = self.current_trial()
        if trial is None:
            return
        if action_id == f"email_reply_sent_stimulus_{trial.stimulus_id}":
            self._finish_trial(naturally=True)

    def skip_trial(self) -> None:
        self._finish_trial(naturally=False)

    def _enter_trial(self) -> None:
        trial = self.current_trial()
        if trial is None:
            self.session_finished.emit()
            return
        self._timer.start(TRIAL_MAX_DURATION_MS)
        self._attacker_timer.start(self.attacker_offsets_ms[self._ptr])
        self.trial_started.emit(trial)

    def _on_attacker_window(self) -> None:
        trial = self.current_trial()
        if trial is not None:
            self.attacker_window_opened.emit(trial, self.attacker_offsets_ms[self._ptr])

    def _on_timeout(self) -> None:
        self._finish_trial(naturally=False)

    def _finish_trial(self, naturally: bool) -> None:
        trial = self.current_trial()
        if trial is None:
            return
        self._timer.stop()
        self._attacker_timer.stop()
        self.trial_finished.emit(trial, naturally)

        finished_block = trial.block_index
        self._ptr += 1
        next_trial = self.current_trial()
        if next_trial is None:
            self.session_finished.emit()
            return
        if next_trial.block_index != finished_block:
            self.block_break.emit(finished_block)
        self._enter_trial()
