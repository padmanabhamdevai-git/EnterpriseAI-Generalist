"""orders_server.py — a MEDIATOR server: the server IS the security boundary (book 9.11.1).

Exposes order/invoice status from an ERP that has no AI-appropriate boundary.
Service identity (own scoped credential) + server-side authorization.
Every I-SCALE-D dimension is visible in the code.

PRODUCTION shape (MCP SDK):
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("orders")
    @mcp.tool()
    def get_invoice_status(invoice_id: str) -> dict: ...   # Caller from request context

Here the tools are plain functions taking an explicit Caller, so the identity
flow is visible in one signature and the chapter runs without the SDK. The
authorization/logging logic is identical to production.
"""
from __future__ import annotations

from audit import audit_log
from auth import Caller, require_scope
from erp_client import erp


def get_invoice_status(invoice_id: str, caller: Caller) -> dict:
    """Return payment status for one invoice the caller is entitled to see.

    Use this to answer 'has invoice X been paid?'. Returns status, amount,
    due date, and owning cost center. Does NOT return line items. Refuses
    invoices outside the caller's cost centers.
    """
    # A — Authorization, step 3: scope gate (only the server knows tool→scope)
    require_scope(caller, "invoices:read")

    # S/E — fetch via the SCOPED service credential. The credential could read
    # any invoice; authorization (step 4) is what constrains THIS caller.
    invoice = erp.get_invoice(invoice_id)

    # A — step 4: the fine-grained rule only the server can know.
    # E — errors don't distinguish 'not found' from 'forbidden' (no info leak).
    if invoice is None or invoice.cost_center not in caller.cost_centers:
        audit_log(caller, "get_invoice_status", {"invoice_id": invoice_id},
                  decision="deny", reason="not_found_or_forbidden")
        raise ValueError("Invoice not found or not accessible.")

    # C — tight result schema: only what the tool promises.
    result = {"invoice_id": invoice.id, "status": invoice.status,
              "amount": invoice.amount, "currency": invoice.currency,
              "due_date": invoice.due_date, "cost_center": invoice.cost_center}

    # L — log the allowed invocation with identity, args, decision, result.
    audit_log(caller, "get_invoice_status", {"invoice_id": invoice_id},
              decision="allow", result_summary=invoice.status)
    return result


# The tool registry the gateway routes into (production: the SDK does this).
TOOLS = {"get_invoice_status": get_invoice_status}
TOOL_SCOPES = {"get_invoice_status": "invoices:read"}
