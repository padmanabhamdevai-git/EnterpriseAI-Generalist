"""guards.py — the reliability controls agents specifically need (book 11.5.4 / 11.11).

The Agent class in agent.py implements step limit, loop detection, and the
autonomy gate inline for legibility. This module factors out the two guards
you'd share across agents in a real codebase: a cost budget and a wall-clock
timeout. All guards FAIL SAFE — they escalate to a human, never silently
truncate or proceed unprotected.
"""
import time


class CostBudget:
    """Track cumulative token cost across steps; trip when exceeded.

    A cost budget is both a cost control (caps the runaway-loop bill) and a
    safety/anomaly signal (an agent burning far more than its peers is
    misbehaving). On trip: escalate — never silently continue.
    """

    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used = 0

    def add(self, tokens: int) -> None:
        self.used += tokens

    def exceeded(self) -> bool:
        return self.used > self.max_tokens


class Timeout:
    """Wall-clock guard: an agent that runs too long (a hung tool, a slow
    loop) trips and escalates rather than hanging forever."""

    def __init__(self, max_seconds: float):
        self.deadline = time.monotonic() + max_seconds

    def exceeded(self) -> bool:
        return time.monotonic() > self.deadline


def loop_signature(action: str, args: dict) -> str:
    """Stable signature for loop detection: same action + same args = stuck.
    (agent.py inlines this; exposed here for reuse and testing.)"""
    import json
    return f"{action}:{json.dumps(args, sort_keys=True)}"


if __name__ == "__main__":
    b = CostBudget(max_tokens=1000)
    b.add(400); b.add(400)
    print("after 800:", "OK" if not b.exceeded() else "TRIP")
    b.add(400)
    print("after 1200:", "OK" if not b.exceeded() else "TRIP → escalate")

    assert loop_signature("get_order", {"id": "A"}) == loop_signature("get_order", {"id": "A"})
    assert loop_signature("get_order", {"id": "A"}) != loop_signature("get_order", {"id": "B"})
    print("loop signature: identical args match, different args differ — OK")
