"""quote_to_order.py — the supervised multi-agent system (book 12.11.3).

Supervisor + specialists + collective PACT + system-wide trust plane.
The consequential action (booking) is concentrated in the supervisor, behind
a human gate — the conflicting-actions and emergent-misbehavior defenses.
"""
from orchestrator import Specialist, Supervisor, SystemGuards
from specialists import ops_agent, pricing_agent, product_agent

# The COLLECTIVE PACT, as the supervisor's purpose (§12.9 step 4).
COLLECTIVE_PURPOSE = """You coordinate a sales team to produce a complete,
priced, feasible quote for a customer configuration, then (on human approval)
book the order.
Delegate to: product (validate config), pricing (price vs. contract), ops
(confirm inventory + lead time). When you have all three, assemble their
findings into a quote and finish.
You are a COORDINATOR: delegate to specialists; do not do their work yourself;
hold the plan and authorize only the final action.
Non-goals (ESCALATE): orders over $500K; non-standard discounts; any lead time
ops hasn't confirmed. You may PRODUCE the quote autonomously; BOOKING requires
human approval — never book without it."""

SPECIALISTS = [
    Specialist("product", "Validates and details the product configuration. Read-only.",
               product_agent),
    Specialist("pricing", "Prices the config against the customer's contract. "
               "Proposes pricing; never commits.", pricing_agent),
    Specialist("ops", "Confirms inventory and lead time. Read-only.", ops_agent),
]


def run_quote(request: str, book_approval=lambda quote: False) -> dict:
    guards = SystemGuards(max_delegations=15, max_tokens=50_000)  # SYSTEM budget
    supervisor = Supervisor(COLLECTIVE_PURPOSE, SPECIALISTS, guards)
    result = supervisor.run(request)

    # Booking = the consequential collective action, concentrated + gated.
    if result["outcome"] == "complete":
        quote = result["quote"]
        result["booked"] = bool(book_approval(quote))
        if not result["booked"]:
            result["note"] = "quote produced; booking awaits human approval"
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("QUOTE-TO-ORDER: supervised team produces a quote (booking gated)")
    print("=" * 70)
    out = run_quote(
        "Customer ACME wants a quote for a FlowGuard-2-Pro configuration. "
        "Validate it, price it against their contract, and confirm feasibility.",
        book_approval=lambda quote: False,   # human declines/defers booking
    )
    print(f"\noutcome: {out['outcome']}")
    print("\n--- UNIFIED TRACE (the system-wide trust plane) ---")
    for entry in out.get("trace", []):
        for who, what in entry.items():
            print(f"  [{who}] {str(what)[:90]}")
    if out["outcome"] == "complete":
        print(f"\nbooked: {out['booked']}  ({out.get('note', '')})")
        print("\nNote: no specialist could book. Booking is concentrated in the")
        print("supervisor behind a human gate — so the SYSTEM's autonomy is")
        print("'produce the quote alone, book only with approval'.")
