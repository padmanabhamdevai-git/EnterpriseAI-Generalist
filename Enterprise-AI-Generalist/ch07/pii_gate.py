"""pii_gate.py — link 3's gate: scan before anything is embedded (book 7.11.3).

Two layers: fast deterministic patterns (cheap, catches the unambiguous),
then LLM screening for the ambiguous middle (names-in-context, quasi-
identifiers). Verdicts: PASS / QUARANTINE (owner review) — never silent drop.

The gate runs at PROCESSING, before embedding: vectors are not encryption,
and un-embedding a leak is not a thing.
"""
import re

from ai_client import ask

PATTERNS = {  # the unambiguous layer — extend per jurisdiction
    "ssn":   re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    "iban":  re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
    "card":  re.compile(r"\b(?:\d[ -]?){15,16}\b"),
}

SCREEN_RUBRIC = (
    "You are a privacy screening service for an enterprise knowledge base "
    "that should contain POLICY and PROCEDURE text, never individual records. "
    "Given a chunk, answer with exactly one word, PASS or QUARANTINE:\n"
    "- QUARANTINE if it contains information about an identifiable individual "
    "(names with personal details, salaries, health, performance, case records).\n"
    "- PASS if names appear only as document owners, approvers, or authors, "
    "or as fictional examples.\nWhen unsure, QUARANTINE."
)


def scan_chunk(text: str) -> tuple[str, list[str]]:
    """Returns (verdict, reasons). Deterministic layer first; LLM only
    when patterns are clean — the cheap check gates the expensive one."""
    hits = [name for name, rx in PATTERNS.items() if rx.search(text)]
    if hits:
        return "QUARANTINE", [f"pattern:{h}" for h in hits]

    verdict = ask(text[:2000], system=SCREEN_RUBRIC,
                  provider="openai", temperature=0.0, max_tokens=5).text.strip()
    if verdict not in ("PASS", "QUARANTINE"):
        verdict = "QUARANTINE"               # unparseable = fail safe
    return verdict, [] if verdict == "PASS" else ["llm:screening"]


TEST_CHUNKS = [
    # clean policy text → PASS
    ("Expense reports must be submitted within 30 days of trip completion. "
     "Reports after 90 days require CFO approval.", "PASS"),
    # unambiguous PII → QUARANTINE (pattern layer)
    ("Contact the payroll team at payroll-ops@meridian.example with your "
     "banking details.", "QUARANTINE"),
    # individual record → QUARANTINE (LLM layer)
    ("Case note: employee J. Rivera (badge 44127) was placed on a performance "
     "improvement plan on March 3 following the Q1 review.", "QUARANTINE"),
    # name as approver → PASS (LLM layer must not over-trigger)
    ("This procedure was approved by R. Okafor, Director of Legal Operations, "
     "and takes effect June 1.", "PASS"),
    # fictional example → PASS
    ("Example: if Dana books a flight over eight hours, Dana's cost-center "
     "director must approve in advance.", "PASS"),
]

if __name__ == "__main__":
    correct = 0
    for text, expected in TEST_CHUNKS:
        verdict, reasons = scan_chunk(text)
        ok = verdict == expected
        correct += ok
        mark = "OK  " if ok else "MISS"
        print(f"{mark} {verdict:>10}  ({','.join(reasons) or 'clean'})  "
              f"{text[:55]}...")
    print(f"\n{correct}/{len(TEST_CHUNKS)} verdicts as expected.")
    print("Tune the rubric toward YOUR quarantine-review capacity (Exercise 5).")
