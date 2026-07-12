"""blueprint.py — the Enterprise AI Architecture Blueprint as data; the request
trace as code (Chapter 18, sections 18.5, 18.6, 18.11.1).

Seven layers + the governance plane, Meridian's estate mapped onto them, and
the boundary validator: the checks that catch layer-spanning violations —
credentials above Layer 4, knowledge outside Layer 5, direct model calls
bypassing Layer 6, components invisible to the plane.

Runs standalone: no API keys.

    python blueprint.py
"""
from dataclasses import dataclass, field

LAYERS = ["experience", "agent", "orchestration", "integration",
          "knowledge", "model", "data"]          # + the plane, which crosses all

LAYER_CONTRACTS = {
    "experience":    "renders, collects, routes — holds NO credentials, NO logic",
    "agent":         "judgment within PACT bounds; consequential actions live in tools",
    "orchestration": "reliable composition (TIER-R); no business logic, no raw credentials",
    "integration":   "THE BRIGHT LINE: every crossing to systems of record, mediated + logged",
    "knowledge":     "one platform API; retrieval with entitlements; no per-tool silos",
    "model":         "one gateway; right-sized routing; no direct vendor calls elsewhere",
    "data":          "systems of record stay authoritative; AI writes arrive marked",
}

REQUIRED_HOOKS = {"identity", "logs"}   # the plane's minimum: unobservable = not done


@dataclass
class Component:
    name: str
    layer: str
    built_in_chapter: str = ""
    holds_credentials: bool = False     # only integration (doors) may, above Layer 7
    calls_models_directly: bool = False # only the model gateway may
    stores_knowledge: bool = False      # only the knowledge layer may
    plane_hooks: set[str] = field(default_factory=set)
    owner: str = ""


def validate(components: list[Component]) -> list[str]:
    findings = []
    for c in components:
        if c.layer not in LAYERS:
            findings.append(f"{c.name}: unknown layer '{c.layer}'")
            continue
        if c.holds_credentials and c.layer != "integration":
            findings.append(f"{c.name} [{c.layer}]: holds credentials above Layer 4 — "
                            "the first brick of the second estate")
        if c.calls_models_directly and c.layer != "model":
            findings.append(f"{c.name} [{c.layer}]: calls model vendors directly — "
                            "key sprawl; route through the gateway")
        if c.stores_knowledge and c.layer != "knowledge":
            findings.append(f"{c.name} [{c.layer}]: private knowledge silo — "
                            "same doc, five staleness clocks, zero entitlements")
        missing = REQUIRED_HOOKS - c.plane_hooks
        if missing:
            findings.append(f"{c.name} [{c.layer}]: missing plane hooks {sorted(missing)} — "
                            "a component that can't be observed isn't done")
        if not c.owner:
            findings.append(f"{c.name} [{c.layer}]: no owner — the plane's oldest rule")
    return findings


# ---------------------------------------------------------------------------
# Meridian's estate, mapped (the book's builds, placed) — plus three planted
# violations per section 18.9 Step 2's standard findings.
# ---------------------------------------------------------------------------
FULL = {"identity", "logs", "evals", "budget"}

MERIDIAN_ESTATE = [
    Component("Mira (RMA voice line)", "experience", "Ch. 14", plane_hooks=FULL, owner="support dir"),
    Component("Install Companion app", "experience", "Ch. 15", plane_hooks=FULL, owner="product"),
    Component("Support agent", "agent", "Ch. 11", plane_hooks=FULL, owner="support dir"),
    Component("Quote-to-order system", "agent", "Ch. 12", plane_hooks=FULL, owner="sales ops"),
    Component("Workflow engine (62 workflows)", "orchestration", "Ch. 10", plane_hooks=FULL, owner="automation team"),
    Component("Media pipeline", "orchestration", "Ch. 17", plane_hooks=FULL, owner="brand + platform"),
    Component("API mgmt + MCP gateway (doors)", "integration", "Ch. 8-9",
              holds_credentials=True, plane_hooks=FULL, owner="platform group"),
    Component("Knowledge platform", "knowledge", "Ch. 5-7",
              stores_knowledge=True, plane_hooks=FULL, owner="platform group"),
    Component("Model gateway", "model", "Ch. 2, 4",
              calls_models_directly=True, plane_hooks=FULL, owner="platform group"),
    Component("SAP / SFDC / SNOW / data platform", "data", "(the estate)",
              plane_hooks={"identity", "logs"}, owner="respective app owners"),
    # --- the three planted violations (18.9 Step 2's standard findings) ---
    Component("Sales team chat widget (found in amnesty)", "experience", "",
              calls_models_directly=True, holds_credentials=True,
              plane_hooks=set(), owner=""),
    Component("Legal dept doc-QA tool (vendor SaaS)", "agent", "",
              stores_knowledge=True, plane_hooks={"identity"}, owner="legal ops"),
    Component("CRM copilot's ERP connector (vendor convenience)", "agent", "",
              holds_credentials=True, plane_hooks={"logs"}, owner="CRM admin"),
]


if __name__ == "__main__":
    print("THE ENTERPRISE AI ARCHITECTURE BLUEPRINT (Chapter 18)\n")
    print("LAYER CONTRACTS:")
    for layer in LAYERS:
        print(f"  L{LAYERS.index(layer)+1} {layer:<14} {LAYER_CONTRACTS[layer]}")
    print(f"  +  governance plane crosses all: identity · registers · policy · evals · observability · cost\n")

    print("MERIDIAN'S ESTATE, MAPPED:")
    for c in MERIDIAN_ESTATE:
        badge = f"({c.built_in_chapter})" if c.built_in_chapter else "(amnesty find)"
        print(f"  L{LAYERS.index(c.layer)+1} {c.layer:<14} {c.name:<44} {badge}")

    print("\nBOUNDARY VALIDATOR (the request trace as code):")
    findings = validate(MERIDIAN_ESTATE)
    for f in findings:
        print(f"  [!] {f}")
    print(f"\n{len(findings)} finding(s) across 3 amnesty components — Step 2's standard")
    print("findings on schedule: the layer-spanning widget, the knowledge silo, the")
    print("vendor bypass. The map is just their display; the findings ARE the gap analysis.")
