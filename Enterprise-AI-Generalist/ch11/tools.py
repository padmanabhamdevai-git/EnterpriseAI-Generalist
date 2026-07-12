"""tools.py — the agent's tools + autonomy map (book 11.11.2).

In production these are the governed MCP servers of Chapter 9. Here they're
stubs, but the AUTONOMY tags are the real design output of PACT's A dimension:
which tools the agent may use alone, which need a human.
"""
from agent import Tool

# Stub backends (production: the Ch.9 order/knowledge/refund servers).
_ORDERS = {
    "ORD-8891": {"item": "ThermaSense 4", "value": 180, "status": "returned"},
    "ORD-9002": {"item": "FlowGuard 2", "value": 900, "status": "returned"},
}
_POLICY = {
    "defective-unit": "Defective units: full refund OR replacement, no restocking "
                      "fee. Refunds over $200 require manager approval.",
    "wrong-item": "Wrong item returned: replacement at no charge once correct item "
                  "is received; no refund unless the customer requests cancellation.",
    "fee-dispute": "Restocking fee disputes: waive the 15% fee only if the unit was "
                   "confirmed defective; otherwise the fee stands.",
}


def _get_order(args):
    o = _ORDERS.get(args.get("order_id"))
    return str(o) if o else "order not found"


def _search_policy(args):
    return _POLICY.get(args.get("category"), "no policy found for that category")


def _issue_refund(args):
    # The governed tool ENFORCES the limit — the first law (Ch.9). The agent's
    # judgment is checked by the tool, not trusted. Over-limit → refused,
    # agent escalates. Even a manipulated agent cannot over-refund.
    if args.get("amount", 0) > 200:
        return "REFUSED: refunds over $200 require manager approval (escalate)"
    return f"refund of ${args.get('amount')} issued for {args.get('order_id')}"


def _escalate(args):
    return f"ESCALATED to human queue: {args.get('reason', 'unspecified')}"


# The tool set = the agent's power AND its boundary. Note the autonomy tags.
RETURNS_TOOLS = [
    Tool("get_order", "Look up an order by order_id. Returns item, value, status.",
         _get_order, autonomy="full"),                       # read → full
    Tool("search_policy", "Get the return policy for a category "
         "(defective-unit, wrong-item, fee-dispute).", _search_policy, "full"),
    Tool("issue_refund", "Issue a refund. args: order_id, amount, reason. "
         "Refunds over $200 are refused and must be escalated.",
         _issue_refund, autonomy="approval"),                # write → Copilot
    Tool("escalate", "Hand off to a human. args: reason.", _escalate, "full"),
]
