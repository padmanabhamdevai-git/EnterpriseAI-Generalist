"""model_compare.py — a minimal evaluation harness for the Selection Matrix (2.11.3).

Runs a task set against multiple providers; reports accuracy, latency, and tokens.
This is the seed of the evaluation pipeline of Chapter 20 — and the only
legitimate source for the Capability score in the Selection Matrix.

Design decisions (explained in the book):
- temperature 0: evaluation wants repeatability
- exact-match scoring on constrained outputs: start simple, grade later
- misses printed in full: the misses teach more than the score
"""
import time
from dataclasses import dataclass, field

from ai_client import ask  # Chapter 1's wrapper — see ch02/README.md for path setup

# --- The evaluation set: representative tasks WITH known-good answers ---------
EVAL_SET = [
    {
        "id": "classify-1",
        "prompt": "Classify this support ticket into exactly one of "
                  "[billing, technical, account, other]. Ticket: 'I was charged "
                  "twice for my March subscription.' Answer with the category only.",
        "expected": "billing",
    },
    {
        "id": "extract-1",
        "prompt": "Extract the PO number from: 'Please expedite PO-2026-004417, "
                  "the vendor is waiting.' Answer with the PO number only.",
        "expected": "PO-2026-004417",
    },
    {
        "id": "reason-1",
        "prompt": "A PO is approved for 10,000 EUR. Invoices of 4,200 EUR and "
                  "5,900 EUR have been paid against it. A new invoice arrives for "
                  "1,100 EUR. Should it auto-approve under the PO limit? "
                  "Answer yes or no only.",
        "expected": "no",  # 4200 + 5900 + 1100 = 11,200 > 10,000 — intentional trap
    },
]

SYSTEM = "You are a precise enterprise data assistant. Follow output instructions exactly."


@dataclass
class ProviderResult:
    """Aggregated evaluation results for one provider."""

    provider: str
    correct: int = 0
    total: int = 0
    latencies: list = field(default_factory=list)
    tokens_out: int = 0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0


def run(providers: tuple = ("openai", "anthropic")) -> list[ProviderResult]:
    """Run the evaluation set against each provider; return aggregated results."""
    results = []
    for provider in providers:
        r = ProviderResult(provider=provider)
        for case in EVAL_SET:
            start = time.perf_counter()
            resp = ask(case["prompt"], system=SYSTEM, provider=provider,
                       temperature=0.0, max_tokens=30)
            r.latencies.append(time.perf_counter() - start)
            r.tokens_out += resp.output_tokens
            r.total += 1
            got = resp.text.strip().lower().rstrip(".")
            if got == case["expected"].lower():
                r.correct += 1
            else:
                print(f"  MISS [{provider}/{case['id']}]: "
                      f"expected '{case['expected']}', got '{resp.text.strip()}'")
        results.append(r)
    return results


if __name__ == "__main__":
    print(f"Running {len(EVAL_SET)} tasks per provider...\n")
    for r in run():
        avg_ms = 1000 * sum(r.latencies) / len(r.latencies)
        print(f"{r.provider:<12} accuracy {r.accuracy:.0%}   "
              f"avg latency {avg_ms:,.0f} ms   output tokens {r.tokens_out}")
    print("\nThree tasks is a demo. Forty is a selection tool. Four hundred is a")
    print("regression suite — and Chapter 20 shows how to get there.")
