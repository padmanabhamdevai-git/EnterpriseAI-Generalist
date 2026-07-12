"""scorecard.py — C-FIT-S platform selection as a reviewable artifact (Chapter 13, section 13.11.1).

The point of putting the Selection Matrix (Ch. 2) in code is not arithmetic — it is
that profiles, weights, and score rationales become reviewable, diffable artifacts
instead of a spreadsheet someone emails around. Every score carries its evidence
string; a score without evidence fails validation.

Runs standalone: no API keys, no network.

    python scorecard.py
"""
from dataclasses import dataclass, field

DIMENSIONS = ("C", "F", "I", "T", "S")
DIMENSION_NAMES = {
    "C": "Capability (on OUR tasks, tested)",
    "F": "Financials (TCO model, incl. exit reserve)",
    "I": "Integration (our doors, gateway, IdP)",
    "T": "Trust (data terms, certs, claims TESTED)",
    "S": "Scale & speed",
}


@dataclass
class Score:
    value: int          # 1-5
    evidence: str       # REQUIRED: pilot result, document, or measurement — never "seems good"

    def __post_init__(self):
        if not 1 <= self.value <= 5:
            raise ValueError(f"score must be 1-5, got {self.value}")


@dataclass
class TaskProfile:
    name: str
    description: str
    weights: dict[str, int]                 # must sum to 100
    revisit_triggers: list[str] = field(default_factory=list)

    def __post_init__(self):
        if set(self.weights) != set(DIMENSIONS):
            raise ValueError(f"{self.name}: weights must cover exactly {DIMENSIONS}")
        if sum(self.weights.values()) != 100:
            raise ValueError(
                f"{self.name}: weights sum to {sum(self.weights.values())}, not 100"
            )


@dataclass
class Candidate:
    name: str
    family: str                             # one of the five families — classify BEFORE you evaluate
    scores: dict[str, Score]

    def weighted_total(self, profile: TaskProfile) -> float:
        for dim in DIMENSIONS:
            if dim not in self.scores:
                raise ValueError(f"{self.name}: missing score for dimension {dim}")
            if not self.scores[dim].evidence.strip():
                raise ValueError(f"{self.name}/{dim}: score without evidence is theater")
        return round(
            sum(profile.weights[d] * self.scores[d].value for d in DIMENSIONS) / 100, 2
        )


def sensitivity(profile: TaskProfile, candidates: list[Candidate]) -> list[str]:
    """Would the leader change if any single weight shifted by +/-10?

    If yes, the decision is weight-sensitive — argue the weights harder before
    deciding. A selection that flips when one weight moves ten points is not a
    selection; it is a coin toss wearing a spreadsheet.
    """
    notes: list[str] = []
    base = max(candidates, key=lambda c: c.weighted_total(profile)).name
    for dim in DIMENSIONS:
        for delta in (+10, -10):
            w = dict(profile.weights)
            if not 0 <= w[dim] + delta <= 100:
                continue
            # shift delta from/to the largest other weight, keeping the sum at 100
            other = max((d for d in DIMENSIONS if d != dim), key=lambda d: w[d])
            if not 0 <= w[other] - delta <= 100:
                continue
            w[dim] += delta
            w[other] -= delta
            trial = TaskProfile(profile.name, profile.description, w)
            leader = max(candidates, key=lambda c: c.weighted_total(trial)).name
            if leader != base:
                notes.append(f"{dim}{delta:+d} (taken from {other}) flips the leader to {leader}")
    return notes or ["decision is robust to +/-10 weight shifts"]


def run_selection(profile: TaskProfile, candidates: list[Candidate]) -> None:
    print("=" * 76)
    print(f"PROFILE {profile.name}: {profile.description}")
    print("-" * 76)
    print("  weights: " + "  ".join(f"{d}={profile.weights[d]}" for d in DIMENSIONS))
    print()
    ranked = sorted(candidates, key=lambda c: c.weighted_total(profile), reverse=True)
    for i, c in enumerate(ranked):
        marker = "  <-- LEADER" if i == 0 else ""
        cells = " ".join(f"{d}{c.scores[d].value}" for d in DIMENSIONS)
        print(f"  {c.name:<28} [{c.family:<18}] {cells}  ->  {c.weighted_total(profile):.2f}{marker}")
    print()
    print("  sensitivity:")
    for note in sensitivity(profile, candidates):
        print(f"    - {note}")
    if profile.revisit_triggers:
        print("  revisit triggers:")
        for t in profile.revisit_triggers:
            print(f"    - {t}")
    print()


if __name__ == "__main__":
    from profiles import MERIDIAN_SELECTIONS

    print("C-FIT-S PLATFORM SELECTION — Meridian's three task profiles (section 13.9)")
    print("One matrix per task profile. Never one matrix for 'the enterprise'.\n")
    for profile, candidates in MERIDIAN_SELECTIONS:
        run_selection(profile, candidates)
    print("Compute, then ARGUE: the weighted total identifies the leader; the argument")
    print("about the scores is where decision quality comes from. Record the decision")
    print("with evidence, date, and revisit triggers — and open the Portability Ledger")
    print("the same day (portability_ledger.py).")
