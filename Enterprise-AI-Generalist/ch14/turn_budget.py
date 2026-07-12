"""turn_budget.py — where the milliseconds go (Chapter 14, sections 14.7, 14.11.1).

The Turn Budget: the time between the caller's last word and the agent's first
audio, budgeted component by component against the conversational comfort window.
Under the window, the agent interrupts callers; over it, callers say "hello?".

Runs standalone: no API keys, no audio hardware.

    python turn_budget.py
"""
from dataclasses import dataclass

COMFORT_WINDOW_MS = (900, 1500)   # practitioner consensus, roughly: under = interruptions; over = dead air


@dataclass
class Component:
    name: str
    p50_ms: int
    p95_ms: int
    note: str = ""


def budget(components: list[Component]) -> dict:
    p50 = sum(c.p50_ms for c in components)
    p95 = sum(c.p95_ms for c in components)     # worst-case stack-up: the caller remembers p95
    lo, hi = COMFORT_WINDOW_MS
    verdict = ("TOO FAST — will interrupt callers (answering pauses, not turns)" if p50 < lo else
               "OVER BUDGET — callers will say 'hello? are you there?'" if p95 > hi else
               "in the window")
    return {"p50_ms": p50, "p95_ms": p95, "verdict": verdict}


def report(title: str, components: list[Component]) -> None:
    print("=" * 78)
    print(title)
    print("-" * 78)
    for c in components:
        note = f"   <- {c.note}" if c.note else ""
        print(f"  {c.name:<52} p50 {c.p50_ms:>5}  p95 {c.p95_ms:>5}{note}")
    b = budget(components)
    lo, hi = COMFORT_WINDOW_MS
    print("-" * 78)
    print(f"  {'TOTAL (first audio after caller stops)':<52} p50 {b['p50_ms']:>5}  p95 {b['p95_ms']:>5}")
    print(f"  comfort window: {lo}-{hi} ms   ->   {b['verdict']}")
    print()


FRONTIER_UNTUNED = [        # the demo that felt fine in the office
    Component("endpointing (turn detection)", 500, 700),
    Component("STT finalization", 100, 200),
    Component("LLM first token (frontier model, long prompt)", 600, 1100, "the big lever"),
    Component("TTS first byte (non-streaming)", 400, 700, "waits for the WHOLE reply"),
    Component("network / telephony transit", 150, 300, "cross-region hairpin"),
]

FAST_TUNED = [              # the same agent after the section 14.7 levers
    Component("endpointing (balanced preset, tuned on golden calls)", 400, 550),
    Component("STT finalization (streaming partials)", 60, 120),
    Component("LLM first token (fast tier, lean prompt)", 250, 430, "right-sized via C-FIT-S"),
    Component("TTS first byte (streaming)", 120, 200, "speaks on the first clause"),
    Component("network / telephony (regional endpoint)", 100, 150),
]

OVER_TUNED = [              # the cautionary third stack: don't tune BELOW the window
    Component("endpointing (most aggressive preset)", 200, 300, "answers pauses, not turns"),
    Component("STT finalization (streaming partials)", 60, 120),
    Component("LLM first token (fast tier, lean prompt)", 250, 450),
    Component("TTS first byte (streaming)", 120, 220),
    Component("network / telephony (regional endpoint)", 100, 150),
]


if __name__ == "__main__":
    print("THE TURN BUDGET (section 14.7)")
    print("Voice latency is a portfolio problem: no single component is the villain.\n")
    report("STACK 1 — frontier model, defaults (the untuned pilot)", FRONTIER_UNTUNED)
    report("STACK 2 — fast tier, fully streamed, regional (the 14.20 tuning story)", FAST_TUNED)
    report("STACK 3 — over-tuned (the cautionary tale)", OVER_TUNED)
    print("levers, in order of leverage: stream everything; right-size the model;")
    print("regional endpoints; mask tool calls with a filler line ('let me check that')")
    print("— and do NOT tune below the window: accuracy over speed, every single call.")
    print("\nNote: tool calls (calendar, ERP) add 1-3 s that no model choice fixes —")
    print("that time is masked by the filler line, not budgeted here.")
