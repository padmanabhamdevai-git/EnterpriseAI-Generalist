"""maturity.py — the Enterprise AI Capability Maturity Model: locate honestly,
build the next rung (Chapter 20, sections 20.8, 20.12.3).

Five levels, each built on the one below. The value is diagnostic AND
prescriptive: your level, and the ONE next thing to build — which is always
the highest-leverage build, because it is what the level above depends on.

The book itself is the sequence of next-rungs: the gateway (Ch. 2) is the
1->2 move, the platform (Chs. 7-18) is 2->3, this chapter's operations are
3->4, the improve flywheel is 4->5.

Runs standalone: no API keys.

    python maturity.py
"""

LEVELS = {
    1: ("Ad-hoc", "individual pilots, no shared platform, no governance, no ops",
        "build the first shared component — the model gateway (Ch. 2)"),
    2: ("Repeatable", "some shared infra, inconsistent adoption, governance written not enforced",
        "stand up the platform group and ENFORCE the plane — the gateway/doors become the default path"),
    3: ("Defined", "platform operates the shared layers, governance enforced, AIDLC standard",
        "build operational maturity — the unified trace, continuous evals, FinOps (this chapter)"),
    4: ("Managed", "estate observable + evaluated + cost-managed; drift caught; four signals flow",
        "close the improve loop systematically — from watched to improving-on-purpose"),
    5: ("Optimizing", "the improve flywheel runs; AI is core infrastructure operated as a discipline",
        "apply the model reflexively; ship platform improvements as a product"),
}

# each marker belongs to a level; your level is the highest tier ALL of whose
# markers hold, with every lower tier also fully satisfied (the no-skipping rule)
MARKERS = {
    2: ["a shared model gateway exists and most teams use it",
        "some governance is written down"],
    3: ["a platform group operates the shared layers and governance is ENFORCED (a gate, not a suggestion)",
        "new capabilities inherit the platform and its controls by default"],
    4: ["a unified trace follows a request across layers",
        "evaluations run continuously (on change, on schedule, on sample)",
        "cost per outcome is known per system"],
    5: ["production learning systematically feeds design (the improve loop is a standing rhythm)"],
}


def assess(answers: dict[str, bool]) -> tuple[int, str, str]:
    """Highest tier all of whose markers are True, with every lower tier also
    fully satisfied. Enforces the no-skipping discipline of section 20.8."""
    level = 1
    for tier in (2, 3, 4, 5):
        if all(answers.get(m, False) for t in range(2, tier + 1) for m in MARKERS[t]):
            level = tier
        else:
            break   # a gap here means you can't be at any higher level (no skipping)
    name, desc, next_step = LEVELS[level]
    return level, f"{name} — {desc}", next_step


# Meridian at the end of Chapter 20: Level 4, climbing (the improve loop is
# a discipline they're building, not one they have).
MERIDIAN = {
    "a shared model gateway exists and most teams use it": True,
    "some governance is written down": True,
    "a platform group operates the shared layers and governance is ENFORCED (a gate, not a suggestion)": True,
    "new capabilities inherit the platform and its controls by default": True,
    "a unified trace follows a request across layers": True,
    "evaluations run continuously (on change, on schedule, on sample)": True,
    "cost per outcome is known per system": True,
    "production learning systematically feeds design (the improve loop is a standing rhythm)": False,
}


if __name__ == "__main__":
    print("THE ENTERPRISE AI CAPABILITY MATURITY MODEL (section 20.8)\n")
    for lvl in range(1, 6):
        name, desc, nxt = LEVELS[lvl]
        print(f"  L{lvl} {name:<12} {desc}")
    print()
    level, summary, next_step = assess(MERIDIAN)
    print(f"MERIDIAN'S SELF-ASSESSMENT -> LEVEL {level}: {summary}")
    print(f"  NEXT RUNG: {next_step}\n")
    print("The no-skipping rule: you cannot claim Level 4's observability while failing")
    print("Level 3's enforced platform — the higher capability assumes the lower one.")
    print("The sentence the model exists to produce: your level, and the one next thing.")
