from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from session_config import BlockSpec, build_block_sequence, generate_sensitive_content, SensitiveContent


@dataclass(frozen=True)
class StepSpec:
    step_id: str
    max_duration_ms: int   
    screen: str            
    completes_on: str       
                            


STEP_SEQUENCE: list[StepSpec] = [
    StepSpec("read_email", 15_000, "email", "tab:banking"),
    StepSpec("navigate_to_banking", 8_000, "banking", "tab:banking"),
    StepSpec("bank_login", 18_000, "banking", "action:bank_login_success"),
    StepSpec("bank_pay", 24_000, "banking", "action:bank_payment_confirmed"),
    StepSpec("navigate_to_health", 8_000, "health", "tab:health"),
    StepSpec("health_login", 18_000, "health", "action:health_login_success"),
    StepSpec("health_booking", 28_000, "health", "action:appointment_confirmed"),
    StepSpec("navigate_to_gov", 8_000, "gov", "tab:gov"),
    StepSpec("gov_login", 18_000, "gov", "action:gov_login_success"),
    StepSpec("gov_menu", 10_000, "gov", "action:gov_menu_signature_selected"),
    StepSpec("gov_select_document", 15_000, "gov", "action:gov_signature_requested"),
    StepSpec("check_email_otp", 15_000, "email", "action:otp_email_opened"),
    StepSpec("gov_enter_otp", 18_000, "gov", "action:otp_correct"),
    StepSpec("return_to_email", 8_000, "email", "tab:email"),
]


class BlockSequencer(QObject):

    block_started = pyqtSignal(int, str, bool)   
    step_started = pyqtSignal(str, str)          
    block_finished = pyqtSignal(int)
    session_finished = pyqtSignal()
    step_completed = pyqtSignal(str, bool)

    def __init__(self, session_id: str, counterbalance_offset: int = 0,
                 profile_id: str = "A", parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.profile_id = profile_id
        self.blocks: list[BlockSpec] = build_block_sequence(session_id, counterbalance_offset)
        self.content: SensitiveContent = generate_sensitive_content(
            session_id, profile_id=profile_id)

        self._block_ptr = 0
        self._step_ptr = 0
        self._active_tab = "email"
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    #  public API
    def start(self) -> None:
        self._block_ptr = 0
        self._step_ptr = 0
        self._active_tab = "email"
        self._emit_block_started()
        self._enter_step()

    def stop(self) -> None:
        """Σταματά τον χρονιστή βήματος. Χρειάζεται όταν η συνεδρία διακόπτεται
        πρόωρα: αλλιώς ο χρονιστής συνεχίζει να μετρά και εκπέμπει step_completed
        για παράθυρο που έχει ήδη κλείσει."""
        self._timer.stop()

    def current_block(self) -> BlockSpec:
        return self.blocks[self._block_ptr]

    def current_step(self) -> StepSpec:
        return STEP_SEQUENCE[self._step_ptr]

    def notify_tab_changed(self, screen_name: str) -> None:
        self._active_tab = screen_name
        self._try_complete(f"tab:{screen_name}")

    def notify_action(self, action_id: str) -> None:
        self._try_complete(f"action:{action_id}")

    # internals
    def _try_complete(self, satisfied_key: str) -> None:
        if self._block_ptr >= len(self.blocks) or self._step_ptr >= len(STEP_SEQUENCE):
            return
        if STEP_SEQUENCE[self._step_ptr].completes_on != satisfied_key:
            return
        self._timer.stop()
        self.step_completed.emit(STEP_SEQUENCE[self._step_ptr].step_id, True)
        if self._advance_pointer():
            self._enter_step()

    def _on_timeout(self) -> None:
        if self._step_ptr < len(STEP_SEQUENCE):
            self.step_completed.emit(STEP_SEQUENCE[self._step_ptr].step_id, False)
        if self._advance_pointer():
            self._enter_step()

    def _advance_pointer(self) -> bool:
        self._step_ptr += 1
        if self._step_ptr >= len(STEP_SEQUENCE):
            finished_index = self.blocks[self._block_ptr].block_index
            self.block_finished.emit(finished_index)

            self._block_ptr += 1
            self._step_ptr = 0

            if self._block_ptr >= len(self.blocks):
                self.session_finished.emit()
                return False

            self._emit_block_started()
        return True

    def _enter_step(self) -> None:
        while self._step_ptr < len(STEP_SEQUENCE):
            step = STEP_SEQUENCE[self._step_ptr]
            kind, _, value = step.completes_on.partition(":")
            if kind == "tab" and self._active_tab == value:
                self.step_completed.emit(step.step_id, True)
                if not self._advance_pointer():
                    return
                continue
            break

        if self._step_ptr < len(STEP_SEQUENCE):
            step = STEP_SEQUENCE[self._step_ptr]
            self._timer.start(step.max_duration_ms)
            self._emit_step_started()

    def _emit_block_started(self) -> None:
        block = self.blocks[self._block_ptr]
        cid = "baseline" if block.is_baseline else block.condition.condition_id
        self.block_started.emit(block.block_index, cid, block.is_baseline)

    def _emit_step_started(self) -> None:
        step = STEP_SEQUENCE[self._step_ptr]
        self.step_started.emit(step.step_id, step.screen)
