"""solution_canvas.py — the Enterprise AI Solution Canvas as an intake bar
(Chapter 15, sections 15.5, 15.11.1).

Seven boxes — Problem, Users, Data, Model, Integration, Risk, Value — plus the
thin slice and the kill criteria. Evidence required in every box. The validator's
error strings are the chapter's aphorisms on purpose: the intake bar teaches
while it filters.

Runs standalone: no API keys.

    python solution_canvas.py
"""
from dataclasses import dataclass, field


@dataclass
class Evidence:
    claim: str
    source: str          # link, ticket query, review, dataset — something checkable
    date: str            # evidence ages; an undated complaint is folklore


@dataclass
class SolutionCanvas:
    name: str
    # Box 1 — Problem
    problem: str
    problem_evidence: list[Evidence]
    # Box 2 — Users
    primary_user: str                        # never "everyone"
    journey_moment: str
    # Box 3 — Data
    data_sources: list[dict]                 # {source, owner, rights, freshness}
    # Box 4 — Model
    model_task_profile: str                  # feeds C-FIT-S (Ch. 2)
    seed_eval: str                           # the dozen real cases, named
    # Box 5 — Integration
    integrations: list[str]                  # each mapped to a governed door (Ch. 9)
    # Box 6 — Risk
    risk_quadrant: str                       # the Leverage Grid position (Ch. 1)
    risk_notes: list[str] = field(default_factory=list)
    # Box 7 — Value
    value_metric: str = ""                   # metric, baseline, delta
    sponsor: str = ""                        # a named human who wants this
    commodity_check: str = ""                # "why is this not a purchase?"
    # Beneath the boxes
    thin_slice: str = ""                     # ONE vertical cut, riskiest assumption first
    kill_criteria: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        p = []
        if not self.problem_evidence:
            p.append("Box 1: no observable evidence — this is a pitch, not a canvas")
        for e in self.problem_evidence:
            if not e.source.strip() or not e.date.strip():
                p.append(f"Box 1: evidence '{e.claim[:40]}...' lacks source/date — undated complaints are folklore")
        if any(w in self.primary_user.lower() for w in ("everyone", "anybody", "all users", "any user")):
            p.append("Box 2: 'everyone' is not a user — name someone you could recruit 20 of this week")
        for d in self.data_sources:
            if d.get("rights", "unknown").lower() in ("unknown", "unclear", "scraped", "tbd"):
                p.append(f"Box 3: data source '{d['source']}' has no confirmed rights — "
                         "no gate can fix a product built on data you may not use")
        if not self.seed_eval.strip():
            p.append("Box 4: no seed evaluation named — you cannot pilot what you cannot measure")
        if not self.sponsor.strip():
            p.append("Box 7: no sponsor — an unwanted product is a hobby")
        if not self.commodity_check.strip():
            p.append("Box 7: commodity check missing — answer 'why is this not a purchase?' in one honest sentence")
        if not self.thin_slice.strip():
            p.append("thin slice missing — name the ONE vertical cut that attacks the riskiest box")
        if not self.kill_criteria:
            p.append("kill criteria missing — a canvas that can't say what kills it is a pitch")
        return p

    def report(self) -> bool:
        problems = self.validate()
        print("=" * 78)
        print(f"CANVAS: {self.name}")
        print(f"  problem: {self.problem[:70]}")
        print(f"  user: {self.primary_user[:70]}")
        print(f"  sponsor: {self.sponsor or '(none)'}")
        print("-" * 78)
        if problems:
            for x in problems:
                print(f"  [REJECTED] {x}")
            print("  => canvas REJECTED at intake — fix honestly or record the death")
        else:
            print("  [ok] all seven boxes evidenced; thin slice and kill criteria present")
            print(f"  thin slice: {self.thin_slice[:74]}")
            for k in self.kill_criteria:
                print(f"  kill if: {k}")
            print("  => canvas ACCEPTED for review-board consideration")
        print()
        return not problems


if __name__ == "__main__":
    from canvases import INSTALL_COMPANION, ERROR_LOG_DIAGNOSER, MEETING_SUMMARIZER

    print("THE ENTERPRISE AI SOLUTION CANVAS — Meridian's sprint intake (section 15.9)\n")
    results = {c.name: c.report() for c in (INSTALL_COMPANION, ERROR_LOG_DIAGNOSER, MEETING_SUMMARIZER)}
    accepted = [n for n, ok in results.items() if ok]
    print(f"{len(accepted)}/{len(results)} canvases pass intake: {', '.join(accepted) or '(none)'}")
    print("\nNote: the summarizer PASSES validation — its death comes at the review board,")
    print("where the commodity-check answer ('three vendors sell this') is read aloud.")
    print("The validator filters unevidenced pitches; the BOARD kills evidenced-but-buyable ideas.")
