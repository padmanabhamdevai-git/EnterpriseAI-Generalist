"""private_pipeline.py — the pipeline with zero egress (book 4.11.3).

Same stages, same schemas, same gates — routed to a local model via the
Chapter 2 pattern. Includes the capability comparison the Private AI
Decision Path's step 3 requires: run both planes on the same eval set,
print per-plane accuracy, latency, and schema-repair rate.

Prerequisite:  ollama pull llama3.2   (and Ollama running)

The routing table expresses privacy posture as data, not scattered ifs:
for the deal-room variant, ROUTES_PRIVATE is the only legal table.
"""
import time

from ai_client import ask
from local_model import ask_local
from structured_output import extract_validated
from eval_notes import EVAL_NOTES


def ask_local_adapter(prompt: str, system: str = "", provider: str = "ignored",
                      temperature: float = 0.0, max_tokens: int = 500):
    """Adapt ask_local() to the ask() signature so stages can be re-routed
    without touching their logic. 'provider' is accepted and ignored —
    the route IS the provider."""
    return ask_local(prompt, system=system, temperature=temperature,
                     max_tokens=max_tokens)


# --- Routing tables: the privacy posture as data --------------------------------
ROUTES_HOSTED = {"extract": ask}
ROUTES_PRIVATE = {"extract": ask_local_adapter}
# Hybrid example (extract local, judgment hosted) — legal only if the data
# class permits the hosted leg:
ROUTES_HYBRID = {"extract": ask_local_adapter}


def run_plane(name: str, routes: dict) -> None:
    """Run the extraction stage across the eval set on one plane; score it."""
    correct = 0
    repairs = 0
    latencies = []

    print(f"\n=== plane: {name} ===")
    for i, (note, expected) in enumerate(EVAL_NOTES, 1):
        start = time.perf_counter()
        attempts_before = _count_attempts()
        try:
            facts = extract_validated(note, ask_fn=routes["extract"])
        except RuntimeError:
            print(f"  note {i:>2}: FAILED (exhausted retries) → human queue")
            latencies.append(time.perf_counter() - start)
            continue
        latencies.append(time.perf_counter() - start)

        ok = (facts.defect_category.value == expected["defect_category"]
              and facts.defect_confirmed == expected["defect_confirmed"])
        correct += ok
        if not ok:
            print(f"  note {i:>2}: MISS — got "
                  f"{facts.defect_category.value}/{facts.defect_confirmed}, "
                  f"expected {expected['defect_category']}/"
                  f"{expected['defect_confirmed']}")

    n = len(EVAL_NOTES)
    avg_s = sum(latencies) / len(latencies) if latencies else 0
    print(f"\n{name:<10} accuracy {correct}/{n} ({correct/n:.0%})   "
          f"avg latency {avg_s:>5.1f}s per note")


def _count_attempts() -> int:
    """Placeholder hook: in production, repair counts come from telemetry.
    extract_validated prints attempts; wire a counter here when you
    industrialize (Chapter 20)."""
    return 0


if __name__ == "__main__":
    print(f"Comparing planes on {len(EVAL_NOTES)} notes "
          f"(traps at #7, #9, #11)...")
    run_plane("hosted", ROUTES_HOSTED)
    run_plane("private", ROUTES_PRIVATE)
    print(
        "\nRead the gap with Chapter 2 eyes: extraction parity is common,\n"
        "judgment gaps are real, and repair rates differ. These numbers,\n"
        "on YOUR documents, are the local-AI debate made empirical.\n"
        "For the zero-egress demonstration: re-run the private plane with a\n"
        "network monitor attached — that session is your privacy-counsel demo."
    )
