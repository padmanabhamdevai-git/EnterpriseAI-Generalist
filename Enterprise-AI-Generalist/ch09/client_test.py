"""client_test.py — exercise both servers, entitled and under-entitled (book 9.10).

Runs standalone with mock tokens and stubs. Demonstrates:
- the MEDIATOR (orders) enforcing the cost-center rule in the server
- the WRAPPER (knowledge) delegating to RLS via token exchange
- coarse authz at the gateway (catalog policy) vs. fine authz in the server
- every path logged with the HUMAN's identity, allow and deny
"""
from auth import make_mock_token
from gateway import handle_invocation


def banner(title: str) -> None:
    print("\n" + "=" * 68 + f"\n{title}\n" + "=" * 68)


if __name__ == "__main__":
    # Priya: procurement analyst, may reach orders + knowledge, CC-PROCUREMENT.
    priya = make_mock_token(
        subject="priya@meridian.example", host="procurement-assistant",
        scopes=["invoices:read", "knowledge:read"], cost_centers=["CC-PROCUREMENT"])

    # A support agent: knowledge only, no invoice scope, different cost center.
    support = make_mock_token(
        subject="sam@meridian.example", host="support-desktop",
        scopes=["knowledge:read"], cost_centers=["CC-SUPPORT"])

    banner("1 · MEDIATOR — Priya checks an invoice IN her cost center (ALLOW)")
    print(handle_invocation(priya, "orders", "get_invoice_status",
                            {"invoice_id": "INV-4411"}))

    banner("2 · MEDIATOR — Priya checks an EXEC invoice (DENY: cost-center rule)")
    try:
        handle_invocation(priya, "orders", "get_invoice_status",
                          {"invoice_id": "INV-9001"})
    except ValueError as e:
        print(f"refused (and logged): {e}")

    banner("3 · COARSE AUTHZ — support-desktop may NOT reach 'orders' (catalog)")
    try:
        handle_invocation(support, "orders", "get_invoice_status",
                          {"invoice_id": "INV-4411"})
    except PermissionError as e:
        print(f"gateway refused: {e}")

    banner("4 · MEDIATOR — support has no invoices:read scope (DENY: scope)")
    # (Even if the catalog allowed it, the scope gate would stop it. Show the
    #  scope gate directly by giving support a fake orders grant:)
    support_with_orders = make_mock_token(
        subject="sam@meridian.example", host="procurement-assistant",  # borrow host
        scopes=["knowledge:read"], cost_centers=["CC-SUPPORT"])
    try:
        handle_invocation(support_with_orders, "orders", "get_invoice_status",
                          {"invoice_id": "INV-4411"})
    except PermissionError as e:
        print(f"scope gate refused: {e}")

    banner("5 · WRAPPER — Priya asks a policy question (delegated → RLS answers)")
    print(handle_invocation(priya, "knowledge", "search_knowledge",
                            {"question": "How many days can I work abroad?"}))

    banner("6 · WRAPPER — non-HR user asks an HR-only question (RLS refuses)")
    print(handle_invocation(support, "knowledge", "search_knowledge",
                            {"question": "How are exception approvals logged?"}))

    print("\n" + "-" * 68)
    print("Every invocation above logged the HUMAN's identity, allow AND deny.")
    print("Mediator: cost-center rule in the server. Wrapper: RLS via delegation.")
    print("Coarse authz (catalog) at the gateway; fine authz in the server.")
