"""tco_model.py — the five-line TCO and the credit crossover (Chapter 13, sections 13.7, 13.11.2).

TCO = License/credits + Model spend + Infrastructure + People + Exit reserve

The credit crossover: platform credits are a markup on someone else's compute plus
a rounding of your usage into the vendor's units. Convenient at prototype scale;
multiplied at production scale. This module makes the crossover visible for YOUR
numbers — the parameters are inputs, not predictions.

Runs standalone: no API keys, no network.

    python tco_model.py
"""
from dataclasses import dataclass


def monthly_model_cost(runs: int, calls_per_run: int, tokens_per_call: int,
                       direct_price_per_mtok: float, credit_markup: float) -> dict:
    """Compare the same model workload billed directly vs. through platform credits.

    credit_markup: the effective multiple over direct API rates once credit bundling
    is unwound — MEASURE it from the vendor's credit schedule (credits per model call
    x dollars per credit / direct API cost of that call). A 3-5x range was typical
    for this platform generation; verify against current pricing.
    """
    mtok = runs * calls_per_run * tokens_per_call / 1_000_000
    direct = mtok * direct_price_per_mtok
    return {
        "million_tokens": round(mtok, 1),
        "direct_usd": round(direct, 2),
        "credits_usd": round(direct * credit_markup, 2),
        "monthly_penalty_usd": round(direct * (credit_markup - 1), 2),
    }


@dataclass
class TCOLine:
    label: str
    monthly_usd: float
    note: str = ""


def five_line_tco(lines: list[TCOLine]) -> None:
    """Print the five-line model. The discipline is that ALL FIVE lines appear —
    especially People (almost always dominant) and Exit reserve (almost always
    omitted). A comparison missing either line is marketing, not analysis."""
    required = {"license/credits", "model spend", "infrastructure", "people", "exit reserve"}
    labels = {l.label.lower() for l in lines}
    missing = required - labels
    if missing:
        raise ValueError(f"TCO missing required lines: {sorted(missing)} — "
                         "a comparison without them is marketing, not analysis")
    total = sum(l.monthly_usd for l in lines)
    for l in lines:
        note = f"   ({l.note})" if l.note else ""
        print(f"    {l.label:<18} ${l.monthly_usd:>10,.0f}{note}")
    print(f"    {'TOTAL':<18} ${total:>10,.0f} / month")


if __name__ == "__main__":
    print("THE CREDIT CROSSOVER (section 13.7.2)")
    print("workload: 40 model calls/run x 6,000 tokens/call; markup 4.0x (measure your own)\n")
    print(f"{'runs/mo':>8} {'Mtok':>8} {'direct':>10} {'credits':>11} {'penalty':>11}")
    for runs in (100, 500, 2_000, 20_000):   # prototype -> pilot -> daily automation -> production
        r = monthly_model_cost(runs, calls_per_run=40, tokens_per_call=6_000,
                               direct_price_per_mtok=1.00, credit_markup=4.0)
        print(f"{runs:>8} {r['million_tokens']:>8} {r['direct_usd']:>10,.0f} "
              f"{r['credits_usd']:>11,.0f} {r['monthly_penalty_usd']:>11,.0f}")
    print("\nreading: below a few hundred runs/month the penalty is pocket change and the")
    print("convenience wins; at a few thousand the penalty funds the BYO-key migration in")
    print("its first month. Flip production workloads to direct billing through your")
    print("gateway (Ch. 2) the day they graduate from prototype.\n")

    print("THE FIVE-LINE TCO (section 13.7.1) — example: sanctioned citizen tier, year one")
    five_line_tco([
        TCOLine("License/credits", 1_800, "seats + non-model credits after BYO-key flip"),
        TCOLine("Model spend", 650, "direct via gateway (was ~2,600 inside credits)"),
        TCOLine("Infrastructure", 0, "SaaS"),
        TCOLine("People", 6_500, "0.3 FTE platform ownership + training amortized"),
        TCOLine("Exit reserve", 900, "ledger reds priced over 24 months"),
    ])
    print("\nnote which line dominates. It is almost never the license line.")
