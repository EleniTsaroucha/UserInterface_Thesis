from __future__ import annotations

import hashlib
import itertools
import random
from dataclasses import dataclass

from mail_stimuli import STIMULUS_IDS

BACKENDS: tuple[str, ...] = ("webcam_mediapipe", "tobii_4c", "tobii_spectrum")
SCENARIOS: tuple[str, ...] = ("S1", "S2", "S3")


DESIGN_CELLS: tuple[tuple[str, str], ...] = tuple(
    (backend, scenario) for backend in BACKENDS for scenario in SCENARIOS
)

BACKEND_ORDERS: tuple[tuple[str, ...], ...] = tuple(itertools.permutations(BACKENDS))


@dataclass(frozen=True)
class Trial:
    trial_index: int      
    block_index: int      
    backend: str
    scenario: str
    stimulus_id: str

    @property
    def trial_id(self) -> str:
        return f"t{self.trial_index}_{self.backend}_{self.scenario}_{self.stimulus_id}"


def _participant_index(session_id: str) -> int:
    digits = "".join(ch for ch in session_id if ch.isdigit())
    if digits:
        return int(digits)
    return int(hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:8], 16)


def stimulus_assignment(session_id: str) -> dict[tuple[str, str], str]:
    p = _participant_index(session_id)
    return {
        cell: STIMULUS_IDS[(j + p) % len(STIMULUS_IDS)]
        for j, cell in enumerate(DESIGN_CELLS)
    }


def build_trial_plan(session_id: str) -> list[Trial]:
    p = _participant_index(session_id)
    assignment = stimulus_assignment(session_id)
    backend_order = BACKEND_ORDERS[p % len(BACKEND_ORDERS)]

    rng = random.Random(
        int(hashlib.sha256(f"{session_id}:scenarios".encode("utf-8")).hexdigest()[:16], 16)
    )

    trials: list[Trial] = []
    for block_index, backend in enumerate(backend_order):
        scenarios = list(SCENARIOS)
        rng.shuffle(scenarios)
        for scenario in scenarios:
            trials.append(Trial(
                trial_index=len(trials),
                block_index=block_index,
                backend=backend,
                scenario=scenario,
                stimulus_id=assignment[(backend, scenario)],
            ))
    return trials


def describe(session_id: str) -> str:
    lines = [f"Πλάνο συνεδρίας {session_id}", "-" * 58,
             f"{'#':>2}  {'block':>5}  {'backend':<18} {'σενάριο':<8} κείμενο"]
    for t in build_trial_plan(session_id):
        lines.append(f"{t.trial_index:>2}  {t.block_index:>5}  {t.backend:<18} "
                     f"{t.scenario:<8} {t.stimulus_id}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe("P07"))
