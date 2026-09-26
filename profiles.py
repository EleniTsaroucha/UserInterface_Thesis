from __future__ import annotations

from dataclasses import dataclass

from session_config import (
    SensitiveContent,
    generate_sensitive_content,
)

PROFILE_IDS: tuple[str, ...] = ("A", "B")

OS_PASSWORDS: dict[str, str] = {
    "A": "1234",
    "B": "5678",
}

PROFILE_DISPLAY: dict[str, tuple[str, str]] = {
    "A": ("Χρήστης Α", "user_a"),
    "B": ("Χρήστης Β", "user_b"),
}


@dataclass(frozen=True)
class Profile:

    profile_id: str
    display_name: str
    account_name: str
    os_password: str
    content: SensitiveContent


def build_profiles(session_id: str) -> dict[str, Profile]:
    profiles: dict[str, Profile] = {}
    for pid in PROFILE_IDS:
        display_name, account_name = PROFILE_DISPLAY[pid]
        profiles[pid] = Profile(
            profile_id=pid,
            display_name=display_name,
            account_name=account_name,
            os_password=OS_PASSWORDS[pid],
            content=generate_sensitive_content(session_id, profile_id=pid),
        )

    a, b = profiles["A"], profiles["B"]
    assert a.os_password != b.os_password
    for field in ("iban", "bank_username", "bank_password", "afm", "amka",
                  "taxis_username", "taxis_password"):
        assert getattr(a.content, field) != getattr(b.content, field), (
            f"Σύγκρουση ευαίσθητου πεδίου '{field}' μεταξύ προφίλ Α και Β"
        )
    return profiles


def assign_profile(session_id: str) -> str:
    digits = "".join(ch for ch in session_id if ch.isdigit())
    index = int(digits) if digits else sum(ord(ch) for ch in session_id)
    return PROFILE_IDS[index % len(PROFILE_IDS)]


def credentials_sheet(session_id: str) -> str:
    lines = [f"ΦΥΛΛΟ ΔΙΑΠΙΣΤΕΥΤΗΡΙΩΝ -- συνεδρία {session_id}", "=" * 58]
    for pid, profile in build_profiles(session_id).items():
        c = profile.content
        lines += [
            "",
            f"[ΠΡΟΦΙΛ {pid}] {profile.display_name}  ({profile.account_name})",
            f"  Κωδικός εισόδου Windows : {profile.os_password}",
            f"  Τράπεζα username        : {c.bank_username}",
            f"  Τράπεζα password        : {c.bank_password}",
            f"  IBAN                    : {c.iban}",
            f"  Υπόλοιπο                : {c.bank_balance_eur} €",
            f"  Taxisnet username       : {c.taxis_username}",
            f"  Taxisnet password       : {c.taxis_password}",
            f"  ΑΦΜ                     : {c.afm}",
            f"  ΑΜΚΑ                    : {c.amka}",
        ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    print(credentials_sheet(sys.argv[1] if len(sys.argv) > 1 else "P07"))
