"""portability_ledger.py — the Portability Ledger as a checkable artifact (Chapter 13, section 13.7.3).

One ledger per platform, opened ON ADOPTION DAY, not compiled in anger at renewal.
Each row covers one lock-in surface (section 13.4.4). Most rows can read
"zero if the rule held" — because Parts I-III already told you to keep prompts in
registries, evals in repos, knowledge in your platform, and access behind your
doors. Portability is the compound interest on discipline you already practiced.

Runs standalone: no API keys, no network.

    python portability_ledger.py
"""
from dataclasses import dataclass

SURFACES = (
    "logic",            # workflows / agent definitions
    "prompts",          # belongs in the prompt registry (Ch. 3), never only in nodes
    "evals",            # belongs in your repo (Ch. 2, 6) — never inside a vendor tool
    "knowledge",        # belongs in the knowledge platform (Ch. 7), not uploads
    "credentials",      # prefer your governed doors (Ch. 9) over platform-held grants
    "run_history",      # stream to your log store continuously
    "people",           # train on concepts (TIER-R, PACT), not buttons
)

STATUS = ("green", "yellow", "red")


@dataclass
class LedgerRow:
    surface: str
    where_it_lives: str
    export_path: str            # "" means none — that is evaluation data
    rebuild_cost: str           # human estimate: "zero", "days", "weeks", "months"
    mitigation: str
    status: str                 # green / yellow / red

    def __post_init__(self):
        if self.surface not in SURFACES:
            raise ValueError(f"unknown surface {self.surface!r}; must be one of {SURFACES}")
        if self.status not in STATUS:
            raise ValueError(f"status must be one of {STATUS}")


@dataclass
class PortabilityLedger:
    platform: str
    family: str
    owner: str                  # every platform has an owner, and the owner has hours
    rows: list[LedgerRow]

    def __post_init__(self):
        covered = {r.surface for r in self.rows}
        missing = set(SURFACES) - covered
        if missing:
            raise ValueError(f"{self.platform}: ledger missing surfaces {sorted(missing)} — "
                             "an incomplete ledger is a red row you haven't found yet")

    def reds(self) -> list[LedgerRow]:
        return [r for r in self.rows if r.status == "red"]

    def report(self) -> None:
        print("=" * 74)
        print(f"PORTABILITY LEDGER — {self.platform}  [{self.family}]  owner: {self.owner}")
        print("-" * 74)
        for r in self.rows:
            flag = {"green": "[G]", "yellow": "[Y]", "red": "[R]"}[r.status]
            print(f"  {flag} {r.surface:<12} lives: {r.where_it_lives:<26} "
                  f"export: {r.export_path or 'NONE':<16} rebuild: {r.rebuild_cost}")
            if r.status != "green":
                print(f"        mitigation: {r.mitigation}")
        reds = self.reds()
        print("-" * 74)
        if reds:
            print(f"  EXIT RESERVE = the {len(reds)} red row(s) above, priced. "
                  "Start the mitigations this week, not at renewal.")
        else:
            print("  No red rows: the exit reserve is small and this platform is "
                  "swappable. That is discipline compounding, not luck.")
        print()


# ---------------------------------------------------------------------------
# Two example ledgers: the disciplined pilot vs. the accreted adoption.
# The same platform category — the difference is entirely in the practices.
# ---------------------------------------------------------------------------
DISCIPLINED = PortabilityLedger(
    platform="Agent studio (scoped pilot)",
    family="agent studio",
    owner="automation platform team (0.2 FTE)",
    rows=[
        LedgerRow("logic", "studio (agent configs)", "config export API", "days",
                  "weekly export job in CI", "yellow"),
        LedgerRow("prompts", "prompt registry (git)", "git", "zero",
                  "registry is source of truth; studio holds copies", "green"),
        LedgerRow("evals", "our repo (12-case set)", "git", "zero",
                  "evals never built inside vendor tools", "green"),
        LedgerRow("knowledge", "our knowledge platform API", "our API", "zero",
                  "no uploads into studio's built-in store", "green"),
        LedgerRow("credentials", "read-only doors only", "re-grant", "days",
                  "no consequential credentials held by studio", "green"),
        LedgerRow("run_history", "streamed to our log store", "continuous", "zero",
                  "log egress configured at setup", "green"),
        LedgerRow("people", "4 builders trained on concepts", "-", "weeks",
                  "training curriculum is PACT/grounding, tool clicks last mile", "green"),
    ],
)

ACCRETED = PortabilityLedger(
    platform="No-code tool (two years of unregistered growth)",
    family="AI-native no-code",
    owner="(none — that is finding #1)",
    rows=[
        LedgerRow("logic", "platform (300+ flows)", "", "months",
                  "begin export/documentation sprint; freeze new consequential flows", "red"),
        LedgerRow("prompts", "pasted into nodes", "", "weeks",
                  "extract to registry as flows are touched", "red"),
        LedgerRow("evals", "none exist", "", "weeks",
                  "build eval sets for the 10 highest-impact flows first", "red"),
        LedgerRow("knowledge", "uploaded into built-in store", "partial export", "months",
                  "re-serve from knowledge platform; treat uploads as cache", "red"),
        LedgerRow("credentials", "47 platform-held OAuth grants", "re-grant", "weeks",
                  "audit scopes; move consequential access behind governed doors", "red"),
        LedgerRow("run_history", "platform only, 90-day window", "manual export", "compliance gap",
                  "configure log egress now; accept the historical gap formally", "red"),
        LedgerRow("people", "2 builders know where buttons are", "-", "months",
                  "concept training; document the flows they carry in their heads", "yellow"),
    ],
)


if __name__ == "__main__":
    print("THE PORTABILITY LEDGER (section 13.7.3)")
    print("Same platform category, two adoption stories. The difference is not the")
    print("vendor - it is whether the Part I-III disciplines were practiced.\n")
    DISCIPLINED.report()
    ACCRETED.report()
    print("Open the ledger on adoption day, when everyone is still friends.")
