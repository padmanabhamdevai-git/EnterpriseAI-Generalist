"""structured_output.py — the Output Reliability Ladder in code (book 4.11.1).

Task: extract structured warranty facts from a free-text inspection note.
R1: ask nicely. R2: validate with Pydantic. R3: repair-and-retry with telemetry.

The single most important line is in extract_validated(): the validator's
error message becomes the next attempt's feedback. Cheap, mechanical,
model-agnostic — and the difference between graceful degradation and a
midnight page.
"""
import json
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

from ai_client import ask  # see ch04/README.md for path setup

INSPECTION_NOTE = (
    "Unit MS-88213 (ThermaSense 4) received 24 June. Bench test confirms "
    "sensor drift of 3.1C above tolerance; board shows no liquid damage. "
    "Purchased 11 Feb 2026, standard 24-month coverage. Customer reported "
    "intermittent readings since May. Recommend replacement of sensor "
    "assembly, part TS4-SA-011."
)


class DefectCategory(str, Enum):
    SENSOR_DRIFT = "sensor_drift"
    BOARD_FAILURE = "board_failure"
    LIQUID_DAMAGE = "liquid_damage"
    NO_DEFECT_FOUND = "no_defect_found"
    OTHER = "other"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InspectionFacts(BaseModel):
    """Inter-stage contract: what EXTRACT must hand to ASSESS.

    Field descriptions are instructions the model reads — the schema does
    part of the prompt's work, and versions with it in the registry.
    """

    unit_id: str = Field(description="The unit/order identifier, e.g. MS-88213")
    defect_category: DefectCategory
    defect_confirmed: bool = Field(
        description="True only if the inspection bench-confirmed the defect"
    )
    replacement_part: str | None = Field(
        default=None, description="Part number if a part was recommended"
    )
    purchase_date: str = Field(description="ISO date YYYY-MM-DD")
    coverage_months: int
    confidence: Confidence
    evidence: str = Field(
        description="Verbatim quote from the note supporting defect_category"
    )


def extract(note: str, *, feedback: str = "", ask_fn=ask) -> str:
    """One extraction attempt. R1 by itself: formatted, unverified.

    ask_fn is injectable so private_pipeline.py can route this stage
    to a local model without touching the logic.
    """
    schema = json.dumps(InspectionFacts.model_json_schema(), indent=2)
    repair = f"\nYour previous attempt failed validation:\n{feedback}\n" if feedback else ""
    return ask_fn(
        f"Extract the inspection facts from this note as JSON matching the "
        f"schema below. Output ONLY the JSON object.{repair}\n"
        f"Schema:\n{schema}\n\nNote:\n{note}",
        system="You are a precise data extraction service. No prose, no markdown fences.",
        provider="openai", temperature=0.0, max_tokens=400,
    ).text


def _strip_fences(raw: str) -> str:
    """Models sometimes wrap JSON in ``` fences despite instructions. Tolerate it."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def extract_validated(note: str, max_attempts: int = 3, ask_fn=ask) -> InspectionFacts:
    """R2 + R3: parse, validate, repair with the error message, bounded retries."""
    feedback = ""
    for attempt in range(1, max_attempts + 1):
        raw = extract(note, feedback=feedback, ask_fn=ask_fn)
        try:
            facts = InspectionFacts.model_validate_json(_strip_fences(raw))
            print(f"  attempt {attempt}: VALID")
            return facts
        except ValidationError as e:
            # Telemetry: in production this counter is a dashboard line.
            print(f"  attempt {attempt}: INVALID — {e.error_count()} error(s)")
            feedback = str(e)  # the validator's message becomes the repair prompt
    raise RuntimeError(
        f"Extraction failed after {max_attempts} attempts — route to human queue"
    )


if __name__ == "__main__":
    print("R1 (raw, unverified):")
    print(extract(INSPECTION_NOTE)[:200], "...\n")

    print("R2+R3 (validated, repaired):")
    facts = extract_validated(INSPECTION_NOTE)
    print(f"\n{facts.model_dump_json(indent=2)}")
    print(f"\nEvidence check — the model's claimed support: {facts.evidence!r}")
    print("R4 is a policy question, not a parsing one: see analysis_pipeline.py")
