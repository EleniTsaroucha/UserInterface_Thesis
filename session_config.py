from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from enum import Enum


class Angle(Enum):
    DEG_0 = 0
    DEG_90 = 90


class Distance(Enum):
    CM_30 = 30
    CM_100 = 100


class Illumination(Enum):
    NORMAL = "normal"
    LOW = "low"


@dataclass(frozen=True)
class Condition:
    angle: Angle
    distance: Distance
    illumination: Illumination

    @property
    def condition_id(self) -> str:
        return f"a{self.angle.value}_d{self.distance.value}_i{self.illumination.value}"


ALL_CONDITIONS: list[Condition] = [
    Condition(angle, distance, illumination)
    for angle in Angle
    for distance in Distance
    for illumination in Illumination
]

assert len(ALL_CONDITIONS) == 8, "Αναμένονται ακριβώς 8 πλήρεις συνθήκες (2x2x2)"


@dataclass(frozen=True)
class BlockSpec:
    block_index: int          
    is_baseline: bool
    condition: Condition | None  


@dataclass(frozen=True)
class SensitiveContent:
    iban: str               
    bank_username: str
    bank_password: str
    bank_balance_eur: str    
    afm: str                
    amka: str                
    taxis_username: str
    taxis_password: str
    sender_company: str
    email_subject: str


def _seeded_rng(seed_key: str) -> random.Random:
    digest = hashlib.sha256(seed_key.encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16)
    return random.Random(seed)


_FAKE_COMPANIES = [
    "Δοκιμαστική ΕΠΕ", "Test Utilities ΑΕ", "Demo Services ΟΕ",
    "Sample Corp ΕΠΕ", "Pilot Systems ΑΕ",
]
_FAKE_SUBJECTS = [
    "Κωδικοί πρόσβασης (προσωπική σημείωση)",
    "Τα στοιχεία μου -- backup",
    "ΥΠΕΝΘΥΜΙΣΗ: κωδικοί για εμένα",
]

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  

IBAN_LENGTH_GR = 27  


def _random_username(rng: random.Random, prefix: str) -> str:
    suffix = "".join(rng.choice("0123456789") for _ in range(4))
    return f"{prefix}{suffix}"


def _random_password(rng: random.Random, length: int = 9) -> str:
    return "".join(rng.choice(_ALPHABET) for _ in range(length))


def _random_digits(rng: random.Random, length: int) -> str:
    return "".join(str(rng.randint(0, 9)) for _ in range(length))


def _profile_seed_key(session_id: str, profile_id: str | None) -> str:
    if profile_id is None:
        return session_id
    return f"{session_id}::profile::{profile_id}"


def generate_os_password(session_id: str, profile_id: str, length: int = 8) -> str:
    rng = _seeded_rng(f"{session_id}::os::{profile_id}")
    return _random_password(rng, length)


def generate_sensitive_content(session_id: str,
                               profile_id: str | None = None) -> SensitiveContent:
    shell_rng = _seeded_rng(f"{session_id}::shell")
    sender_company = _FAKE_COMPANIES[shell_rng.randrange(len(_FAKE_COMPANIES))]
    email_subject = _FAKE_SUBJECTS[shell_rng.randrange(len(_FAKE_SUBJECTS))]

    rng = _seeded_rng(_profile_seed_key(session_id, profile_id))

    iban = "GR" + _random_digits(rng, IBAN_LENGTH_GR - 2)
    assert len(iban) == IBAN_LENGTH_GR

    balance_value = rng.uniform(85.0, 9200.0)
    bank_balance_eur = f"{balance_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return SensitiveContent(
        iban=iban,
        bank_username=_random_username(rng, "user"),
        bank_password=_random_password(rng),
        bank_balance_eur=bank_balance_eur,
        afm=_random_digits(rng, 9),
        amka=_random_digits(rng, 11),
        taxis_username=_random_username(rng, "taxis"),
        taxis_password=_random_password(rng),
        sender_company=sender_company,
        email_subject=email_subject,
    )


def build_block_sequence(session_id: str, counterbalance_offset: int = 0) -> list[BlockSpec]:

    n = len(ALL_CONDITIONS)
    rotated = ALL_CONDITIONS[counterbalance_offset % n:] + ALL_CONDITIONS[:counterbalance_offset % n]

    blocks: list[BlockSpec] = [BlockSpec(block_index=0, is_baseline=True, condition=None)]
    for i, cond in enumerate(rotated, start=1):
        blocks.append(BlockSpec(block_index=i, is_baseline=False, condition=cond))
    return blocks
