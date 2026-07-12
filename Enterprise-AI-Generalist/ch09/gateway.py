"""gateway.py — the MCP-aware gateway, as a TEACHING MODEL (book 9.11.3).

Centralizes what every server would otherwise re-implement: authenticate,
coarse-authorize (catalog policy), throttle, and — above all — log every
invocation in one consistent, auditable place. Fine-grained authorization
happens IN the server (only it knows its semantics).

*** This is a teaching model, NOT production middleware. ***
In a real enterprise you extend your API-management platform (Apigee, SAP
API Management, Kong) with MCP awareness — you do not ship this file.
"""
from __future__ import annotations

from collections import defaultdict

from audit import gateway_log
from auth import validate_token

# --- Catalog policy (Ch. 8): which host may reach which server ---------------
CATALOG_POLICY = {
    "procurement-assistant": {"orders", "knowledge"},
    "support-desktop":       {"knowledge"},
}

# --- Rate limits: the runaway-agent circuit breaker (per host+tool) ----------
_QUOTA = 100                                    # invocations per window (demo)
_counts: dict[tuple[str, str], int] = defaultdict(int)


def may_connect(host: str, server: str) -> bool:
    return server in CATALOG_POLICY.get(host, set())


def check_quota(host: str, tool: str) -> None:
    key = (host, tool)
    _counts[key] += 1
    if _counts[key] > _QUOTA:
        raise PermissionError(f"rate limit exceeded for {host}/{tool}")


# Server registry the gateway routes into.
from orders_server import TOOLS as ORDER_TOOLS
from knowledge_server import TOOLS as KNOWLEDGE_TOOLS

SERVERS = {"orders": ORDER_TOOLS, "knowledge": KNOWLEDGE_TOOLS}


def handle_invocation(raw_token: str, server: str, tool: str, args: dict):
    """One governed door for every invocation."""
    caller = validate_token(raw_token)                    # AuthN, once, at the edge

    if not may_connect(caller.host, server):              # coarse AuthZ (catalog)
        gateway_log(caller, server, tool, decision="deny", reason="not_cataloged")
        raise PermissionError(f"{caller.host} may not reach '{server}'")

    check_quota(caller.host, tool)                        # circuit breaker
    gateway_log(caller, server, tool, args, decision="allow")

    fn = SERVERS[server][tool]                            # fine AuthZ happens inside
    return fn(caller=caller, **args)
