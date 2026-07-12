"""knowledge_server.py — a WRAPPER server: delegate, don't re-implement (book 9.11.2).

Exposes Ch. 6's /ask over MCP. The knowledge platform's RLS (Ch. 7) already
enforces per-user entitlements — so we DELEGATE the user's identity and let
RLS do the authorization. The server adds almost no access logic; that's the
point of wrapping something already governed.

Contrast with orders_server.py: NO cost-center rule, NO scope-to-data logic —
because the downstream enforces all of it, and the delegated token carries the
real user. If the user can't retrieve it directly, the delegated token can't.
"""
from __future__ import annotations

from audit import audit_log
from auth import Caller, exchange_token
from knowledge_client import ask_knowledge


def search_knowledge(question: str, caller: Caller) -> dict:
    """Answer a policy/procedure question from the enterprise knowledge base,
    with citations. Returns only what the CALLER is entitled to see — the
    platform enforces per-user access. Refuses (not fabricates) when the
    answer isn't in the caller's accessible corpus.
    """
    # Delegated identity: exchange the caller's token for a knowledge-scoped
    # token that carries THEIR tiers. The server cannot over-read.
    downstream = exchange_token(caller.token, audience="knowledge-platform")

    answer = ask_knowledge(question, bearer=downstream)   # RLS filters by tier

    audit_log(caller, "search_knowledge", {"question": question},
              decision="allow", result_summary=answer["status"])
    return {"answer": answer["answer"], "citations": answer["citations"],
            "status": answer["status"]}                   # answered|refused|flagged


TOOLS = {"search_knowledge": search_knowledge}
TOOL_SCOPES = {"search_knowledge": "knowledge:read"}
