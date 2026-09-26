from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SensitiveFieldEvent:
    timestamp: float
    session_id: str
    block_index: int
    condition_id: str          
    step_id: str
    sensitive_field_id: str    
    sensitive_value: str
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int


CSV_HEADER = [
    "row_type",
    "timestamp",
    "session_id",
    "block_index",
    "condition_id",
    "step_id",
    "sensitive_field_id",
    "sensitive_value",
    "bbox_x",
    "bbox_y",
    "bbox_w",
    "bbox_h",
    "trial_index",
    "backend",
    "scenario",
    "stimulus_id",
    "profile_id",
]


class SessionLogger:
    def __init__(self, output_dir: Path, session_id: str):
        output_dir.mkdir(parents=True, exist_ok=True)
        self.path = output_dir / f"{session_id}_sensitive_events.csv"
        self._file = open(self.path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(CSV_HEADER)
        self._file.flush()

        self._trial_index: int | str = ""
        self._backend: str = ""
        self._scenario: str = ""
        self._stimulus_id: str = ""
        self._profile_id: str = ""

        self.log_clock_sync(session_id)

    def set_profile(self, profile_id: str) -> None:
        self._profile_id = profile_id

    def set_trial_context(self, trial_index: int, backend: str, scenario: str,
                          stimulus_id: str) -> None:
        self._trial_index = trial_index
        self._backend = backend
        self._scenario = scenario
        self._stimulus_id = stimulus_id

    def clear_trial_context(self) -> None:
        self._trial_index, self._backend, self._scenario, self._stimulus_id = "", "", "", ""

    def _write(self, row: list) -> None:
        self._writer.writerow(
            row + [self._trial_index, self._backend, self._scenario,
                   self._stimulus_id, self._profile_id]
        )
        self._file.flush()  

    def log_clock_sync(self, session_id: str) -> None:
        self._writer.writerow([
            "clock_sync", f"{time.time():.6f}", session_id, "", "", "",
            "perf_counter", f"{time.perf_counter():.6f}", "", "", "", "",
            "", "", "", "", "",
        ])
        self._file.flush()

    def log_field_shown(self, event: SensitiveFieldEvent) -> None:
        self._write([
            "sensitive_field", f"{event.timestamp:.3f}", event.session_id,
            event.block_index, event.condition_id, event.step_id,
            event.sensitive_field_id, event.sensitive_value,
            event.bbox_x, event.bbox_y, event.bbox_w, event.bbox_h,
        ])

    def log_block_boundary(self, session_id: str, block_index: int, condition_id: str,
                           boundary: str) -> None:
        self._write([
            boundary, f"{time.time():.3f}", session_id, block_index, condition_id,
            "", "", "", "", "", "", "",
        ])

    def log_user_action(self, session_id: str, block_index: int, condition_id: str,
                        step_id: str, action_id: str) -> None:
        self._write([
            "user_action", f"{time.time():.3f}", session_id, block_index, condition_id,
            step_id, action_id, "", "", "", "", "",
        ])

    def log_login_event(self, session_id: str, action_id: str, profile_id: str) -> None:
        self._write([
            "os_login", f"{time.time():.3f}", session_id, "", "", "",
            action_id, profile_id, "", "", "", "",
        ])

    def log_step_boundary(self, session_id: str, block_index: int, condition_id: str,
                          step_id: str) -> None:
        self._write([
            "step_started", f"{time.time():.3f}", session_id, block_index, condition_id,
            step_id, "", "", "", "", "", "",
        ])

    def log_step_completion(self, session_id: str, block_index: int, condition_id: str,
                            step_id: str, completed_naturally: bool) -> None:
        self._write([
            "step_completed", f"{time.time():.3f}", session_id, block_index, condition_id,
            step_id, "natural" if completed_naturally else "timeout", "", "", "", "", "",
        ])

    def log_trial_boundary(self, session_id: str, boundary: str) -> None:
        self._write([
            boundary, f"{time.time():.3f}", session_id, "", "", "",
            "", "", "", "", "", "",
        ])

    def log_reply(self, session_id: str, email_id: str, text: str) -> None:
        self._write([
            "email_reply", f"{time.time():.3f}", session_id, "", "", "",
            email_id, text, "", "", "", "",
        ])

    def log_task_answer(self, session_id: str, stimulus_id: str, field_id: str,
                        answer: str, expected: str, correct: bool, is_target: bool) -> None:
        self._write([
            "task_answer", f"{time.time():.3f}", session_id, "", "", stimulus_id,
            field_id, answer, expected, "correct" if correct else "incorrect",
            "target" if is_target else "secondary", "",
        ])

    def close(self) -> None:
        self._file.close()
