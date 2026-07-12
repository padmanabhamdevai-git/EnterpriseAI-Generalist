"""finops.py — cost per OUTCOME, and the four levers in priority order
(Chapter 20, sections 20.7, 20.12.2).

AI has real, controllable unit economics. The levers, in the order that yields
the most savings per unit of effort:
  1. Don't call the model (cache, rules, non-AI paths)
  2. Route to the right model (fast for the mechanical majority)
  3. Compress the context (lean prompts, windowed history, precise retrieval)
  4. Batch and schedule the non-interactive
Measured as cost per OUTCOME, not cost per token.

Runs standalone: no API keys.

    python finops.py
"""
from dataclasses import dataclass


@dataclass
class Workload:
    name: str
    requests_per_month: int
    calls_per_request: int
    tokens_per_call: int
    frontier_price_per_mtok: float
    fast_price_per_mtok: float
    # the levers:
    cache_hit_rate: float = 0.0          # Lever 1: fraction of calls a cache serves
    fast_routable_fraction: float = 0.0  # Lever 2: fraction of remaining calls a fast model handles
    context_trim_fraction: float = 0.0   # Lever 3: fraction of tokens trimmed


def _cost(calls: float, tokens: float, fast_frac: float, w: Workload) -> float:
    mtok = calls * tokens / 1_000_000
    fast = mtok * fast_frac * w.fast_price_per_mtok
    frontier = mtok * (1 - fast_frac) * w.frontier_price_per_mtok
    return fast + frontier


def cost_stages(w: Workload) -> list[tuple[str, float]]:
    """Apply the levers in priority order; report cumulative monthly cost after each."""
    calls = w.requests_per_month * w.calls_per_request
    tokens = w.tokens_per_call
    stages = [("baseline (frontier-everything)", _cost(calls, tokens, 0.0, w))]
    calls1 = calls * (1 - w.cache_hit_rate)
    stages.append(("+ Lever 1: don't call the model (cache)", _cost(calls1, tokens, 0.0, w)))
    stages.append(("+ Lever 2: route to the right model", _cost(calls1, tokens, w.fast_routable_fraction, w)))
    tokens3 = tokens * (1 - w.context_trim_fraction)
    stages.append(("+ Lever 3: compress the context", _cost(calls1, tokens3, w.fast_routable_fraction, w)))
    return [(name, round(c, 2)) for name, c in stages]


def cost_per_outcome(monthly_cost: float, requests_per_month: int) -> float:
    return round(monthly_cost / requests_per_month, 4)


WORKLOAD = Workload(
    name="Install Companion (grounded Q&A at scale)",
    requests_per_month=200_000,
    calls_per_request=2,
    tokens_per_call=3_000,
    frontier_price_per_mtok=5.00,
    fast_price_per_mtok=0.50,
    cache_hit_rate=0.35,           # top error codes answer 35% (Ch. 15's top-40 lesson)
    fast_routable_fraction=0.85,   # 85% is lookup/extraction a fast model handles
    context_trim_fraction=0.30,    # 30% of context was retrieval bloat
)


if __name__ == "__main__":
    print("FINOPS FOR AI — the four levers in priority order (section 20.7)\n")
    print(f"workload: {WORKLOAD.name}  ({WORKLOAD.requests_per_month:,} requests/mo)\n")
    stages = cost_stages(WORKLOAD)
    baseline = stages[0][1]
    for name, cost in stages:
        cpo = cost_per_outcome(cost, WORKLOAD.requests_per_month)
        pct = f"(-{round((1 - cost / baseline) * 100)}% vs baseline)" if cost < baseline else ""
        print(f"  ${cost:>10,.2f}/mo   cost/outcome ${cpo:<8}  {name} {pct}")
    print("\nreading: Levers 1-2 (cache + route) take the majority of the cost out before")
    print("compression fine-tunes the rest — the priority order proves itself. And the")
    print("number that drops in a way the business recognizes is cost per OUTCOME, not")
    print("the token price. Observability pays for itself out of the waste it reveals.")
