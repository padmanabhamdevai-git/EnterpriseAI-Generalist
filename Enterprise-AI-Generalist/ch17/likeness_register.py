"""likeness_register.py — no likeness without documented, scoped, unexpired consent
(Chapter 17, section 17.7.3).

Chapter 14's voice register, generalized: every voice, face, and style the
enterprise may synthesize, with the consent's scope, expiry, and revocation
state. The bright line: not in the register, not generated — no exceptions
for enthusiasm.

Runs standalone: no API keys.

    python likeness_register.py
"""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class LikenessEntry:
    likeness_id: str
    person_or_asset: str
    modality: str                     # voice | face/avatar | style
    consent_doc: str                  # where the signed instrument lives
    permitted_uses: list[str]         # e.g., ["training-modules", "distributor-portal"]
    permitted_channels: list[str]
    expires: date
    compensation: str                 # per-use / licensed-term — never a buyout hidden in an NDA
    revoked: bool = False
    platforms_holding_clone: list[str] = field(default_factory=list)


class LikenessRegister:
    def __init__(self, entries: list[LikenessEntry]):
        self.entries = {e.likeness_id: e for e in entries}

    def consent_valid(self, likeness_id: str, use: str) -> tuple[bool, str]:
        entry = self.entries.get(likeness_id)
        if entry is None:
            return False, "not in the register — not generated, no exceptions for enthusiasm"
        if entry.revoked:
            return False, "consent REVOKED — revocation must actually stop the pipeline"
        if date.today() > entry.expires:
            return False, f"consent EXPIRED {entry.expires} — expiry is the check everyone forgets"
        if use not in entry.permitted_uses:
            return False, f"use '{use}' outside consent scope {entry.permitted_uses}"
        return True, f"consent current and in scope (doc: {entry.consent_doc})"


REGISTER = LikenessRegister([
    LikenessEntry(
        likeness_id="LR-014",
        person_or_asset="Product director (Install Companion presenter)",
        modality="face/avatar + voice",
        consent_doc="legal/consents/LR-014-2026-06.pdf",
        permitted_uses=["training-modules", "distributor-portal"],
        permitted_channels=["LMS", "partner portal"],
        expires=date(2027, 6, 30),
        compensation="licensed-term, annual",
        platforms_holding_clone=["avatar-platform-A"],
    ),
    LikenessEntry(
        likeness_id="LR-009",
        person_or_asset="Former trainer (left the company)",
        modality="face/avatar",
        consent_doc="legal/consents/LR-009-2025-11.pdf",
        permitted_uses=["training-modules"],
        permitted_channels=["LMS"],
        expires=date(2026, 11, 30),
        compensation="licensed-term",
        revoked=True,          # withdrew consent at departure — the register's first revocation (17.20)
    ),
    LikenessEntry(
        likeness_id="LR-002",
        person_or_asset="Narration voice 'Meridian Standard' (licensed synthetic)",
        modality="voice",
        consent_doc="legal/licenses/voice-vendor-agreement.pdf",
        permitted_uses=["training-modules", "product-videos", "distributor-portal"],
        permitted_channels=["all owned channels"],
        expires=date(2026, 3, 31),   # lapsed — renewal missed
        compensation="vendor license",
    ),
])


if __name__ == "__main__":
    print("THE LIKENESS REGISTER (section 17.7.3)")
    print("The bright line: not in the register, not generated.\n")
    checks = [
        ("LR-014", "training-modules", "the consented presenter, in scope"),
        ("LR-014", "paid-social-ads", "the consented presenter, OUT of scope"),
        ("LR-009", "training-modules", "the revoked consent — must stop the pipeline"),
        ("LR-002", "product-videos", "the lapsed vendor license — expiry catches it"),
        ("LR-999", "training-modules", "the likeness nobody registered"),
    ]
    for lid, use, label in checks:
        ok, why = REGISTER.consent_valid(lid, use)
        print(f"  [{'ok  ' if ok else 'STOP'}] {lid} for '{use}' ({label})")
        print(f"         {why}")
    print("\nRevocation executed cleanly in a day is the test most companies fail")
    print("before they know it exists (17.20).")
