"""prompt_registry.py — a file-based prompt registry (book 3.11.3).

Registry = a directory of JSON artifacts under version control.
Each artifact: template + variable schema + model pin + owner + eval evidence.
This IS the pattern platform tools implement; start here, graduate later.

Commit the registry/ directory to Git: diff, blame, review, rollback —
your prompt governance now rides the same rails as your code.
"""
import json
from pathlib import Path

from prompt_template import PromptTemplate, RETURNS_STATUS_EMAIL

REGISTRY_DIR = Path(__file__).parent / "registry"


def save(template: PromptTemplate, *, model_pin: str, owner: str,
         eval_evidence: str, approvals: list[str]) -> Path:
    """Write a template to the registry with its governance metadata."""
    entry = {
        "name": template.name,
        "version": template.version,
        "description": template.description,
        "system": template.system,
        "user": template.user,
        "variables": sorted(template.variables),
        "model_pin": model_pin,          # results only valid for this model (Ch. 2)
        "owner": owner,
        "eval_evidence": eval_evidence,  # path/ref to eval set + results
        "approvals": approvals,          # who signed off (brand, legal, ...)
    }
    path = REGISTRY_DIR / template.name / f"{template.version}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entry, indent=2))
    return path


def load(name: str, version: str) -> PromptTemplate:
    """Load a template by name and exact version. No floating 'latest' in prod."""
    entry = json.loads((REGISTRY_DIR / name / f"{version}.json").read_text())
    return PromptTemplate(
        name=entry["name"], version=entry["version"],
        system=entry["system"], user=entry["user"],
        description=entry["description"],
    )


if __name__ == "__main__":
    path = save(
        RETURNS_STATUS_EMAIL,
        model_pin="claude-sonnet-5",
        owner="returns-ops@meridian.example",
        eval_evidence="evals/returns-status-email/v1.0.0-results.json",
        approvals=["brand:j.liu 2026-06-18", "legal:r.okafor 2026-06-19"],
    )
    print(f"Registered: {path}")

    tpl = load("returns/status-email", "1.0.0")
    print(f"Loaded {tpl.name}@{tpl.version} with variables {sorted(tpl.variables)}")
