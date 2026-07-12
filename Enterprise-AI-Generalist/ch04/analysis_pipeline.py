"""analysis_pipeline.py — chained stages, typed state, R4 gates (book 4.11.2).

The full Figure 4.1 pattern: EXTRACT → ASSESS → DRAFT → CRITIQUE.
- One cognitive job per stage; stages communicate through Pydantic objects.
- rule_gate() is deterministic code that outranks the model: AI proposes,
  code disposes.
- The critique loop is bounded (max 2 revisions) and emits structured
  verdicts — telemetry, not prose.
- The accumulated stage objects ARE the audit trail.
"""
import json

from pydantic import BaseModel, Field, ValidationError

from ai_client import ask
from structured_output import (
    Confidence,
    InspectionFacts,
    _strip_fences,
    extract_validated,
    INSPECTION_NOTE,
)

# --- Warranty policy: business rules live in ONE place ------------------------
WARRANTY_POLICY = (
    "Warranty policy (v2.3):\n"
    "1. Eligibility requires a bench-confirmed defect.\n"
    "2. Coverage runs from purchase date for the stated coverage months.\n"
    "3. Liquid damage voids coverage regardless of other findings.\n"
    "4. Eligible units receive a replacement, never a refund.\n"
)


class WarrantyAssessment(BaseModel):
    """Stage 2 output: the model's judgment, later gated by code."""

    eligible: bool
    rationale: str = Field(description="Two sentences max, citing the facts used")
    rule_citations: list[str] = Field(
        description="Which numbered policy rules were applied"
    )
    requires_human: bool = Field(
        description="True if the case is ambiguous or facts are incomplete"
    )


class CritiqueVerdict(BaseModel):
    criterion: str
    verdict: str = Field(description="'pass' or 'fail'")
    evidence: str = Field(description="Quote from the draft supporting the verdict")


class CritiqueReport(BaseModel):
    verdicts: list[CritiqueVerdict]

    @property
    def failed(self) -> list[CritiqueVerdict]:
        return [v for v in self.verdicts if v.verdict.lower() != "pass"]


def _call_json(prompt: str, system: str, model_cls, max_attempts: int = 3,
               ask_fn=ask, **ask_kwargs):
    """Shared R3 loop: any stage, any schema. The repair pattern, factored once."""
    feedback = ""
    for attempt in range(1, max_attempts + 1):
        repair = f"\nPrevious attempt failed validation:\n{feedback}\n" if feedback else ""
        raw = ask_fn(prompt + repair, system=system, temperature=0.0,
                     max_tokens=600, **ask_kwargs).text
        try:
            return model_cls.model_validate_json(_strip_fences(raw))
        except ValidationError as e:
            feedback = str(e)
    raise RuntimeError(f"{model_cls.__name__} failed after {max_attempts} attempts")


# --- Stage 2: ASSESS -----------------------------------------------------------
def assess(facts: InspectionFacts, ask_fn=ask) -> WarrantyAssessment:
    schema = json.dumps(WarrantyAssessment.model_json_schema(), indent=2)
    return _call_json(
        f"{WARRANTY_POLICY}\n"
        f"Assess warranty eligibility for these inspection facts. "
        f"Output ONLY JSON matching this schema:\n{schema}\n\n"
        f"Facts:\n{facts.model_dump_json(indent=2)}",
        system="You are a warranty assessment service. Apply the policy exactly; "
               "set requires_human=true when facts are incomplete or ambiguous.",
        model_cls=WarrantyAssessment, ask_fn=ask_fn, provider="openai",
    )


# --- R4: deterministic rule gate ------------------------------------------------
def rule_gate(facts: InspectionFacts, a: WarrantyAssessment) -> WarrantyAssessment:
    """Business rules that outrank the model, always.

    Anything the rules can decide, the rules decide — the model's
    eligibility opinion is input, not verdict.
    """
    if not facts.defect_confirmed and a.eligible:
        a.eligible, a.requires_human = False, True
        a.rule_citations.append("GATE: eligibility requires bench-confirmed defect")
    if facts.defect_category.value == "liquid_damage" and a.eligible:
        a.eligible = False
        a.rule_citations.append("GATE: liquid damage voids coverage (rule 3)")
    if facts.confidence == Confidence.LOW:
        a.requires_human = True
        a.rule_citations.append("GATE: low-confidence extraction → human review")
    return a


# --- Stage 3: DRAFT --------------------------------------------------------------
DRAFT_RUBRIC = [
    "states the eligibility outcome in the first paragraph",
    "cites no delivery date or arrival promise",
    "offers no refund (replacement flow only)",
    "under 150 words",
]


def draft(facts: InspectionFacts, a: WarrantyAssessment, ask_fn=ask) -> str:
    return ask_fn(
        f"Write the customer status email for this warranty case.\n"
        f"Facts: {facts.model_dump_json()}\n"
        f"Assessment: {a.model_dump_json()}",
        system="You are a returns specialist at Meridian Systems. Voice: plain, "
               "warm, specific. Rules: " + "; ".join(DRAFT_RUBRIC) + ". "
               "Subject line first, then greeting, three short paragraphs.",
        provider="anthropic", temperature=0.4, max_tokens=400,
    ).text


# --- Stage 4: CRITIQUE ------------------------------------------------------------
def critique(draft_text: str, ask_fn=ask) -> CritiqueReport:
    schema = json.dumps(CritiqueReport.model_json_schema(), indent=2)
    rubric = "\n".join(f"- {c}" for c in DRAFT_RUBRIC)
    return _call_json(
        f"Critique this draft against each rubric criterion. One verdict per "
        f"criterion. Output ONLY JSON matching:\n{schema}\n\n"
        f"Rubric:\n{rubric}\n\nDraft:\n{draft_text}",
        system="You are a strict quality reviewer. Do not praise. "
               "Fail any criterion you cannot verify with a quote.",
        model_cls=CritiqueReport, ask_fn=ask_fn, provider="openai",
    )


# --- Pipeline runner ----------------------------------------------------------------
def run_pipeline(note: str, max_revisions: int = 2) -> dict:
    """Run all four stages; return the audit trail as a dict of stage objects."""
    trail: dict = {"note": note}

    print("Stage 1 · EXTRACT")
    facts = extract_validated(note)
    trail["facts"] = facts.model_dump()

    print("Stage 2 · ASSESS")
    assessment = rule_gate(facts, assess(facts))
    trail["assessment"] = assessment.model_dump()
    if assessment.requires_human:
        trail["outcome"] = "escalated: human queue (with partial state)"
        return trail

    print("Stage 3 · DRAFT")
    text = draft(facts, assessment)

    print("Stage 4 · CRITIQUE")
    for revision in range(max_revisions + 1):
        report = critique(text)
        trail[f"critique_r{revision}"] = report.model_dump()
        if not report.failed:
            break
        print(f"  revision {revision + 1}: {len(report.failed)} criterion failure(s)")
        fixes = "; ".join(f"{v.criterion} (evidence: {v.evidence})" for v in report.failed)
        text = ask(
            f"Revise this draft to fix exactly these failures: {fixes}\n\nDraft:\n{text}",
            system="Revise minimally. Change nothing that passed.",
            provider="anthropic", temperature=0.2, max_tokens=400,
        ).text
    else:
        trail["outcome"] = "escalated: critique loop exhausted"
        return trail

    trail["draft"] = text
    trail["outcome"] = "complete"
    return trail


if __name__ == "__main__":
    trail = run_pipeline(INSPECTION_NOTE)
    print(f"\nOutcome: {trail['outcome']}")
    if "draft" in trail:
        print(f"\n--- FINAL DRAFT ---\n{trail['draft']}")
    print("\n--- AUDIT TRAIL KEYS ---")
    print(list(trail.keys()))
    print("\nEvery stage's validated object is in the trail: the pipeline")
    print("documents itself. That is the design, not a side effect.")
