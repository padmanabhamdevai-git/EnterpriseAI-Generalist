"""prd_render.py — canvas -> PRD skeleton (Chapter 15, sections 15.9 step 4, 15.11.3).

The PRD is the brief you hand to the builders — human or AI. The non-goals
section renders FIRST: builder models fill unspecified gaps with plausible
assumptions (15.4.1), so what the product must NOT do is the highest-value
specification on the page.

Runs standalone: no API keys.

    python prd_render.py
"""
from solution_canvas import SolutionCanvas


def render_prd(c: SolutionCanvas) -> str:
    ev = "\n".join(f"  - \"{e.claim}\" ({e.source}, {e.date})" for e in c.problem_evidence)
    data = "\n".join(f"  - {d['source']} — owner: {d['owner']}; rights: {d['rights']}; "
                     f"freshness: {d['freshness']}" for d in c.data_sources)
    ints = "\n".join(f"  - {i}" for i in c.integrations)
    risks = "\n".join(f"  - {r}" for r in c.risk_notes)
    kills = "\n".join(f"  - {k}" for k in c.kill_criteria)
    return f"""# PRD — {c.name}
*(rendered from the Solution Canvas; expand each section — the blanks are your afternoon's work)*

## 0. NON-GOALS — READ FIRST, BUILDER
The builder (human or AI) must NOT implement anything outside the thin slice.
Known exclusions from the Risk box:
{risks}
> Builder note: every unspecified gap will be filled with a plausible assumption.
> If a capability is not in section 3, it is a non-goal. When in doubt: ask, don't assume.

## 1. Problem (evidence-backed)
{c.problem}
Evidence:
{ev}

## 2. Primary user and journey moment
User: {c.primary_user}
Intercepted moment: {c.journey_moment}

## 3. The thin slice (MVP1 scope — the ONLY scope)
{c.thin_slice}

## 4. Data (grounding)
{data}
Grounding contract: citations mandatory; refusal on out-of-corpus (Ch. 5).

## 5. Model and evaluation
Task profile: {c.model_task_profile}
Seed eval: {c.seed_eval}
The eval bar is a RELEASE GATE, not a report.

## 6. Integration
{ints}
All access through governed doors (Ch. 9). No raw credentials in the build.

## 7. Value and success
Metric: {c.value_metric}
Sponsor: {c.sponsor}
Kill criteria (this product dies if):
{kills}

## 8. Island rules (in force until Gate 1)
Synthetic data only · no real users · git from hour one · secrets in env files ·
plan approved before generation · every merge human-reviewed.
"""


if __name__ == "__main__":
    from canvases import INSTALL_COMPANION
    print(render_prd(INSTALL_COMPANION))
