"""threat_ledger.py — the AI Threat Ledger + the lethal-trifecta check
(Chapter 19, sections 19.5.1, 19.12.1).

Five threat families run against an agent specification; the lethal trifecta
(confidential access + untrusted content + exfiltration in one agent) flagged
first, because it is the single highest-leverage security check in the estate.

Runs standalone: no API keys.

    python threat_ledger.py
"""
from dataclasses import dataclass


@dataclass
class AgentSpec:
    name: str
    reads_untrusted_content: bool   # web, email, docs, tickets it doesn't control
    accesses_confidential: bool     # private data, confidential systems
    can_exfiltrate: bool            # send email, post externally, write to attacker-readable places
    tools_enforce_limits: bool      # consequential actions gated in self-limiting tools (the first law)
    identity: str                   # "delegated" | "service"
    least_privilege: bool
    persistent_memory: bool
    model_source: str               # "gateway-vetted" | "adhoc"


def lethal_trifecta(a: AgentSpec) -> tuple[bool, str]:
    """The single most important check: private data + untrusted content +
    exfiltration in ONE agent is one poisoned page from disaster. Remove a leg."""
    legs = [a.accesses_confidential, a.reads_untrusted_content, a.can_exfiltrate]
    if all(legs):
        return True, ("LETHAL TRIFECTA present: confidential access + untrusted content + "
                      "exfiltration path. Remove one leg — usually the exfiltration ability.")
    return False, f"trifecta safe ({sum(legs)}/3 legs) — no single injection reaches disaster"


def run_ledger(a: AgentSpec) -> list[str]:
    findings = []
    tf, msg = lethal_trifecta(a)
    findings.append(("CRITICAL: " if tf else "ok:       ") + msg)
    if a.reads_untrusted_content and not a.tools_enforce_limits:
        findings.append("INJECTION: reads untrusted content but tools don't self-limit — "
                        "a poisoned input reaches consequential actions")
    if a.accesses_confidential and a.identity == "service":
        findings.append("EXFIL/AGENCY: confidential access on a STANDING service identity — "
                        "prefer delegated identity to inherit the human's least privilege")
    if not a.least_privilege:
        findings.append("AGENCY: not least-privilege — the highest-leverage control is missing; "
                        "every ledger threat's blast radius is uncapped")
    if a.persistent_memory:
        findings.append("POISONING: persistent memory — needs a validated write path (Ch. 12); "
                        "a poisoned memory re-manipulates on every future run")
    if a.model_source != "gateway-vetted":
        findings.append("SUPPLY CHAIN: ad-hoc model source — vet like a dependency (Ch. 16)")
    return findings


def report(a: AgentSpec) -> None:
    print("=" * 76)
    print(f"AGENT: {a.name}")
    for f in run_ledger(a):
        marker = "!!" if f.startswith("CRITICAL") else ("!" if not f.startswith("ok") else " ")
        print(f"  [{marker}] {f}")
    print()


# The quoting assistant (section 19.10) — before and after removing the leg.
QUOTING_BEFORE = AgentSpec(
    name="Quoting assistant (v0 — emails quotes directly)",
    reads_untrusted_content=True,     # distributor RFQs
    accesses_confidential=True,        # pricing knowledge base
    can_exfiltrate=True,               # can email distributors directly  <-- the third leg
    tools_enforce_limits=True,         # booking gated
    identity="delegated",
    least_privilege=True,
    persistent_memory=False,
    model_source="gateway-vetted",
)

QUOTING_AFTER = AgentSpec(
    name="Quoting assistant (v1 — proposes; the rep sends)",
    reads_untrusted_content=True,
    accesses_confidential=True,
    can_exfiltrate=False,              # leg removed: it proposes, a human sends
    tools_enforce_limits=True,
    identity="delegated",
    least_privilege=True,
    persistent_memory=False,
    model_source="gateway-vetted",
)

# A cautionary counter-example: the ungoverned pilot agent.
SHADOW_PILOT = AgentSpec(
    name="Shadow pilot agent (the 'make it work' build)",
    reads_untrusted_content=True,
    accesses_confidential=True,
    can_exfiltrate=True,
    tools_enforce_limits=False,        # limits in the prompt, not the tool
    identity="service",                # broad service account
    least_privilege=False,
    persistent_memory=True,
    model_source="adhoc",
)


if __name__ == "__main__":
    print("THE AI THREAT LEDGER (section 19.5.1)")
    print("Run against every system: which of the five families apply, is each control present?\n")
    report(QUOTING_BEFORE)
    report(QUOTING_AFTER)
    report(SHADOW_PILOT)
    print("The design gate exists to catch the trifecta BEFORE build: v0 -> v1 removed the")
    print("exfiltration leg, so a manipulated assistant can at worst propose a bad quote to")
    print("a human who sees its margin. The shadow pilot is every control missing at once.")
