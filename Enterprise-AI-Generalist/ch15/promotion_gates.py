"""promotion_gates.py — Demo, Pilot, Production, and the two crossings
(Chapter 15, sections 15.7, 15.11.2).

Every build is in exactly one state; each crossing has entry criteria that are
checklists, not vibes. This file replays the Install Companion's history:
five criteria blocking at the first Gate 1 audit, clear nine days later, then
Gate 2's rebuild-shaped list.

Runs standalone: no API keys.

    python promotion_gates.py
"""
from dataclasses import dataclass, field

GATE_1 = {  # Demo -> Pilot: real users and real data are earned, not assumed
    "identity":     "SSO in front; the shareable link is dead",
    "data_rights":  "every Data-box source confirmed in writing for THIS use",
    "eval_v1":      "the seed eval runs and passes its bar — an unevaluated pilot measures nothing",
    "blast_radius": "bounded users, read-mostly access, kill switch, worst-case written down",
    "owner":        "one named human answers when it misbehaves",
}

GATE_2 = {  # Pilot -> Production: the estate inheritance
    "value_proven":   "the pilot moved the Value-box metric against baseline, with numbers",
    "estate_wiring":  "gateway + knowledge platform + governed doors (usually the rebuild moment)",
    "eval_as_gate":   "the suite runs on every change and blocks release (Ch. 6 discipline)",
    "operations":     "monitoring, cost at projected volume, support path, an owner WITH HOURS",
    "compliance":     "disclosure/accessibility/brand/retention closed for the audience",
    "register_entry": "owner, doors, revisit triggers — it joins the inventory like everything else",
}

DEMO_RULES = {  # yes, demos have requirements — the island rules (15.6, 15.18)
    "labeled":      "honestly labeled as a prototype IN THE UI ('prototype — synthetic data')",
    "no_real_data": "no real customer/employee personal data, EVER",
    "secrets_env":  "secrets in env files even here — the habit is the control",
    "in_git":       "in version control from day one",
}

NEVER_SHIPS = [  # the standing answers to "when may a prototype NEVER ship?" (15.7)
    "data rights cannot be secured — no gate fixes data you may not use",
    "error cost sits in the forbidden Leverage Grid quadrant and review can't move it",
    "eval ceiling below the bar and the model class can't close it — keep the canvas, wait",
    "nobody will own it in March",
]


@dataclass
class Build:
    name: str
    state: str                                # demo | pilot | production
    satisfied: set[str] = field(default_factory=set)
    note: str = ""

    def gate_report(self) -> None:
        if self.state == "production":
            print(f"{self.name} [PRODUCTION] — governed by the register entry and revisit triggers")
            if self.note:
                print(f"    note: {self.note}")
            print()
            return
        gate, target = (GATE_1, "PILOT") if self.state == "demo" else (GATE_2, "PRODUCTION")
        blocking = {k: v for k, v in gate.items() if k not in self.satisfied}
        status = "CLEAR TO CROSS" if not blocking else f"{len(blocking)} criteria blocking"
        print(f"{self.name} [{self.state.upper()}] -> {target}: {status}")
        for k in self.satisfied & set(gate):
            print(f"    [x] {k}")
        for k, v in blocking.items():
            print(f"    [ ] {k}: {v}")
        if self.note:
            print(f"    note: {self.note}")
        print()


if __name__ == "__main__":
    print("THE PROTOTYPE PROMOTION GATES — the Install Companion's history (15.9)\n")
    print("Demo-state island rules (always in force):")
    for k, v in DEMO_RULES.items():
        print(f"  - {k}: {v}")
    print()

    Build("Install Companion — first Gate 1 audit (demo-day week)",
          "demo", set(),
          note="the two-session island build: everything still blocking — normal and fine"
          ).gate_report()

    Build("Install Companion — Gate 1 audit, nine days later",
          "demo",
          {"identity", "data_rights", "eval_v1", "blast_radius", "owner"},
          note="SSO wired, scoped read-only door replaced the mock, eval 88% > 85% bar, "
               "20 named installers, support director on the register"
          ).gate_report()

    Build("Install Companion — Gate 2 audit, pilot week six",
          "pilot",
          {"value_proven", "eval_as_gate"},
          note="tickets -31% vs prior quarter; eval wired to CI. Blocking list IS the "
               "rebuild plan: estate wiring, ops, compliance, register"
          ).gate_report()

    Build("Install Companion — production",
          "production", set(),
          note="rebuilt on the estate rails; UI design + grounding contract crossed intact; "
               "revisit trigger: MVP2 when the warranty write door ships"
          ).gate_report()

    print("The standing NEVER-SHIPS list (write it on the wall):")
    for n in NEVER_SHIPS:
        print(f"  x {n}")
    print("\nA prototype that fails these is not a failure — it is two days spent learning")
    print("what would otherwise have cost two quarters.")
