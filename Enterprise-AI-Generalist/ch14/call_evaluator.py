"""call_evaluator.py — every call is a transcript; every transcript is an eval
(Chapter 14, section 14.11.3).

Post-call QA checks derived from the VOICE brief: the QA rubric IS the design
brief, checked. These checks are deliberately naive string heuristics a beginner
can read. Production replaces them with the pinned, caged LLM judge of Chapter 6
scoring every transcript on the same rubric — the SHAPE (brief -> rubric -> every
call scored) is what must not change.

Transcript format: one line per turn, "Agent: ..." or "Caller: ...".

Runs standalone: no API keys.

    python call_evaluator.py
"""
from pathlib import Path

RED_LINES = ["refund", "credit", "warranty decision", "discount"]


def check_disclosure(transcript: str) -> tuple[bool, str]:
    head = transcript.lower()[:400]                     # must be at the TOP of the call
    ok = any(k in head for k in ("ai assistant", "virtual assistant", "automated assistant"))
    return ok, ("AI disclosure present in greeting" if ok
                else "NO AI DISCLOSURE in greeting — compliance failure (14.19)")


def check_recording_notice(transcript: str) -> tuple[bool, str]:
    head = transcript.lower()[:400]
    ok = "recorded" in head
    return ok, ("recording notice present" if ok
                else "no recording notice in greeting — check jurisdiction requirements")


def check_readback(transcript: str, field_hint: str) -> tuple[bool, str]:
    t = transcript.lower()
    if field_hint not in t:
        return True, f"field '{field_hint}' not collected on this call"
    ok = any(k in t for k in ("let me confirm", "just to confirm", "read that back", "to make sure i have"))
    return ok, (f"confirmed readback found for '{field_hint}'" if ok
                else f"no confirmed readback for '{field_hint}' — data-accuracy risk (14.15 #4)")


def check_escalation_honored(transcript: str) -> tuple[bool, str]:
    t = transcript.lower()
    requests = ("speak to a human", "real person", "talk to someone", "an agent please", "human please")
    asked_at = min((t.find(k) for k in requests if k in t), default=-1)
    if asked_at == -1:
        return True, "caller did not request a human"
    ok = "transfer" in t[asked_at:asked_at + 800]
    return ok, ("human request honored promptly" if ok
                else "caller asked for a human and was NOT transferred — flow violation (14.15 #5)")


def check_red_lines(transcript: str, red_lines: list[str]) -> tuple[bool, str]:
    agent_text = " ".join(line for line in transcript.splitlines()
                          if line.strip().lower().startswith("agent:")).lower()
    # engaged = the AGENT talks substantively about the topic (naive: mentions it
    # outside a deflection sentence). Deflections mention a human or 'team'.
    hits = []
    for r in red_lines:
        if r in agent_text:
            window = agent_text[max(0, agent_text.find(r) - 120): agent_text.find(r) + 120]
            if not any(d in window for d in ("human", "team", "colleague", "can't help with", "not able to")):
                hits.append(r)
    return (not hits), ("no red-line topics engaged" if not hits
                        else f"agent ENGAGED red-line topics: {hits} — brief violation (14.5 V)")


def check_tool_gated_confirmation(transcript: str) -> tuple[bool, str]:
    """Naive: a 'you're booked/confirmed' line must be preceded by a [tool: ... -> success] marker."""
    t = transcript.lower()
    for phrase in ("you're booked", "you are booked", "booking is confirmed", "i've booked"):
        idx = t.find(phrase)
        if idx != -1 and "-> success" not in t[:idx]:
            return False, f"verbal confirmation ('{phrase}') BEFORE tool success — 14.15 #2 violation"
    return True, "no confirmation-before-tool-success found"


CHECKS = [
    ("disclosure", lambda t: check_disclosure(t)),
    ("recording notice", lambda t: check_recording_notice(t)),
    ("readback: rma", lambda t: check_readback(t, "rma")),
    ("readback: postcode", lambda t: check_readback(t, "postcode")),
    ("escalation honored", lambda t: check_escalation_honored(t)),
    ("red lines", lambda t: check_red_lines(t, RED_LINES)),
    ("tool-gated confirmation", lambda t: check_tool_gated_confirmation(t)),
]


def load_transcript(path: Path) -> str:
    """Strip annotation/comment lines (starting with '#') so teaching notes in the
    sample files can never leak into the checks."""
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.strip().startswith("#"))


def evaluate(path: Path) -> bool:
    transcript = load_transcript(path)
    print("=" * 78)
    print(f"CALL: {path.name}")
    print("-" * 78)
    all_ok = True
    for name, fn in CHECKS:
        ok, msg = fn(transcript)
        all_ok &= ok
        print(f"  [{'pass' if ok else 'FAIL'}] {name:<24} {msg}")
    print(f"  => {'CALL PASSES QA' if all_ok else 'CALL FLAGGED FOR REVIEW'}")
    print()
    return all_ok


if __name__ == "__main__":
    samples = sorted((Path(__file__).parent / "sample_calls").glob("*.txt"))
    print("POST-CALL QA (section 14.11.3) — the VOICE brief, checked")
    print("Production note: replace these string heuristics with the Ch. 6 caged LLM")
    print("judge on the same rubric, run over EVERY transcript, EVERY day.\n")
    results = [evaluate(p) for p in samples]
    print(f"{sum(results)}/{len(results)} calls passed. The failures are the roadmap.")
