"""arb_package.py — the review-board evidence package: no gate without its evidence
(Chapter 19, sections 19.8 Element 4, 19.10, 19.12.3).

Assembles the evidence a tier requires and refuses to mark the package
review-ready until every required artifact is present — the governance model's
central rule, enforced in code. This is the answer to the director's question:
the board never convenes on an incomplete package.

Runs standalone: no API keys.

    python arb_package.py
"""
from dataclasses import dataclass, field
from risk_tiering import REQUIRED, APPROVAL_AUTHORITY


@dataclass
class ARBPackage:
    system_name: str
    tier: str
    present_evidence: set[str] = field(default_factory=set)

    def add(self, artifact: str) -> None:
        self.present_evidence.add(artifact)

    def review_ready(self) -> tuple[bool, list[str]]:
        required = set(REQUIRED[self.tier]["evidence"])
        missing = required - self.present_evidence
        if missing:
            return False, [f"BLOCKED: {self.tier} tier requires but is missing: {m}"
                           for m in sorted(missing)]
        return True, [f"review-ready: all {len(required)} required artifacts present "
                      f"(approval authority: {APPROVAL_AUTHORITY[self.tier]})"]

    def status(self, label: str) -> None:
        print(f"--- {label} ---")
        ok, msgs = self.review_ready()
        for m in msgs:
            print(f"  {m}")
        print(f"  => {'CONVENE THE BOARD' if ok else 'BOARD DOES NOT CONVENE'}\n")


if __name__ == "__main__":
    print("THE ARB EVIDENCE PACKAGE — no gate without its evidence (section 19.8)\n")
    print(f"Elevated tier requires: {', '.join(REQUIRED['elevated']['evidence'])}\n")

    pkg = ARBPackage("Distributor quoting assistant", tier="elevated")

    # Assemble it the way section 19.10 does, step by step.
    pkg.add("risk classification")       # Step 1: intake gate
    pkg.add("model card")                # Step 3: design documented
    pkg.add("evaluation records")        # Step 4: pre-prod evidence
    pkg.add("approval records")          # (will be produced AT the gate)
    pkg.status("before the threat model is added")

    pkg.add("threat model")              # Step 2: the leg-removing analysis
    pkg.status("after the threat model is added")

    print("The missing threat model kept the board from convening — exactly as designed.")
    print("An elevated system with no threat model is not review-ready, full stop.")
    print("That single rule is the code form of the answer to 'who approved this, on what basis'.")
