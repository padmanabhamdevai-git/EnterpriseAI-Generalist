"""specialists.py — the specialist agents (book 12.11.3).

Each specialist is a narrow, PACT-bounded agent (Ch.11). Here they're
simplified to single-call reasoners over stub tools so the SYSTEM runs
standalone; in production each is a full Ch.11 ReAct agent using the
governed Ch.9 servers.

Note: NONE of the specialists can book the order. Pricing PROPOSES; it never
commits. The consequential action is concentrated in the supervisor (§12.6).
"""
from ai_client import ask

# Stub backends (production: the Ch.9 CRM / pricing / ERP servers).
_CONFIGS = {
    "FlowGuard-2-Pro": {"valid": True, "components": ["base", "hi-flow valve",
                        "redundant sensor"], "list_price": 42000},
}
_CONTRACT = {"ACME": {"discount_pct": 12, "payment_terms": "net-45"}}
_INVENTORY = {"FlowGuard-2-Pro": {"in_stock": 8, "lead_time_days": 21}}


def product_agent(subtask: str, shared_state: dict) -> str:
    """PACT: validate & detail the configuration. Read-only, full autonomy."""
    ctx = f"Known configs: {_CONFIGS}"
    return ask(f"{ctx}\n\nTask: {subtask}\nValidate the configuration and list "
               f"its components and list price. Be concise.",
               system="You are a product configuration specialist. Read-only.",
               temperature=0.0, max_tokens=200).text


def pricing_agent(subtask: str, shared_state: dict) -> str:
    """PACT: price vs. the customer's contract. Read + PROPOSE; never commit."""
    ctx = f"Contract terms: {_CONTRACT}. Product findings: {shared_state['findings'].get('product', 'n/a')}"
    return ask(f"{ctx}\n\nTask: {subtask}\nPROPOSE a price applying the "
               f"customer's contract discount to the list price. State clearly "
               f"this is a PROPOSAL requiring approval. Be concise.",
               system="You are a pricing specialist. You PROPOSE pricing; you "
                      "never commit or book. Only standard contract discounts.",
               temperature=0.0, max_tokens=200).text


def ops_agent(subtask: str, shared_state: dict) -> str:
    """PACT: confirm inventory & lead time. Read-only, full autonomy."""
    ctx = f"Inventory: {_INVENTORY}"
    return ask(f"{ctx}\n\nTask: {subtask}\nConfirm stock and lead time. "
               f"Be concise.",
               system="You are an operations specialist. Read-only.",
               temperature=0.0, max_tokens=150).text
