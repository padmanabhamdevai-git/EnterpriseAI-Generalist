"""risk_tiering.py — the Enterprise AI Governance Model's Element 1
(Chapter 19, sections 19.8, 19.12.2).

The tiering rubric: reversibility, data sensitivity, autonomy, consequence,
regulatory trigger -> a tier -> the gates and evidence that tier requires.
A fast classification at intake, because a slow one gets routed around.

Runs standalone: no API keys.

    python risk_tiering.py
"""
from dataclasses import dataclass

TIERS = ["minimal", "standard", "elevated", "critical"]


@dataclass
class SystemProfile:
    name: str
    reversible: bool          # can a wrong action be undone cheaply?
    data_class: str           # "public" | "internal" | "confidential" | "regulated" | "personal"
    acts_autonomously: bool   # decides/acts without a human in the loop
    consequence: str          # "internal" | "customer" | "money" | "safety" | "protected-decision"
    regulatory_flag: bool     # plausibly high-risk / transparency / data-protection (19.7)


def tier(p: SystemProfile) -> str:
    # a safety consequence or a protected-class decision floors the tier at critical
    if p.consequence in ("safety", "protected-decision"):
        return "critical"
    score = 0
    score += 0 if p.reversible else 2
    score += {"public": 0, "internal": 0, "confidential": 1, "regulated": 2, "personal": 2}[p.data_class]
    score += 2 if p.acts_autonomously else 0
    score += {"internal": 0, "customer": 1, "money": 2}[p.consequence]
    score += 2 if p.regulatory_flag else 0
    return TIERS[0 if score <= 1 else 1 if score <= 3 else 2 if score <= 6 else 3]


REQUIRED = {
    "minimal":  {"gates": ["intake"],
                 "evidence": ["risk classification"]},
    "standard": {"gates": ["intake", "pre-prod"],
                 "evidence": ["risk classification", "model card", "evaluation records"]},
    "elevated": {"gates": ["intake", "design/ARB", "pre-prod", "production", "review"],
                 "evidence": ["risk classification", "threat model", "model card",
                              "evaluation records", "approval records"]},
    "critical": {"gates": ["intake", "design/ARB", "pre-prod", "production", "review"],
                 "evidence": ["risk classification", "threat model", "model card", "evaluation records",
                              "DPIA", "approval records", "sign-off: exec+risk+legal"]},
}

APPROVAL_AUTHORITY = {
    "minimal":  "team lead (self-serve)",
    "standard": "team lead",
    "elevated": "architecture review board (ARB)",
    "critical": "executive + risk + legal body",
}


SYSTEMS = [
    SystemProfile("Internal brainstorm assistant", reversible=True, data_class="internal",
                  acts_autonomously=False, consequence="internal", regulatory_flag=False),
    # elevated, NOT critical (19.10): a human gates every commitment, and the only
    # regulatory hook is transparency (limited-risk), not a high-risk trigger.
    SystemProfile("Distributor quoting assistant", reversible=False, data_class="confidential",
                  acts_autonomously=False, consequence="money", regulatory_flag=False),
    SystemProfile("Loan-decision agent", reversible=False, data_class="personal",
                  acts_autonomously=True, consequence="protected-decision", regulatory_flag=True),
    # the two deliberate surprises (Exercise 2):
    SystemProfile("Customer-email auto-responder (looks harmless)", reversible=False,
                  data_class="personal", acts_autonomously=True, consequence="customer",
                  regulatory_flag=True),
    SystemProfile("Internal 'scary-sounding' code explainer (actually low-risk)", reversible=True,
                  data_class="internal", acts_autonomously=False, consequence="internal",
                  regulatory_flag=False),
]


if __name__ == "__main__":
    print("RISK TIERING — Element 1 of the Enterprise AI Governance Model (section 19.8)\n")
    for p in SYSTEMS:
        t = tier(p)
        print("=" * 76)
        print(f"{p.name}")
        print(f"  -> TIER: {t.upper()}   approval: {APPROVAL_AUTHORITY[t]}")
        print(f"  gates:    {' -> '.join(REQUIRED[t]['gates'])}")
        print(f"  evidence: {', '.join(REQUIRED[t]['evidence'])}")
        print()
    print("Note the surprises: the 'harmless' auto-responder tiers HIGH (autonomous,")
    print("personal data, customer consequence, regulated); the 'scary' code explainer tiers")
    print("MINIMAL (reversible, internal, human-in-loop). And the quoting assistant lands")
    print("ELEVATED not CRITICAL — a human gates every commitment. Tier by factors, not vibe.")
