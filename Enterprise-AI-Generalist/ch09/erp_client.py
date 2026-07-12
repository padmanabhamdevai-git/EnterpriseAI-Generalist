"""erp_client.py — stub ERP behind a 'read-only replica' (book 9.11.1).

Represents the SCOPED service credential (S in I-SCALE-D): this client can
read invoice status and nothing else. In production it holds a service
account with `invoices:read` on a read-only replica — the credential is the
blast-radius ceiling, whatever the model requests.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Invoice:
    id: str
    status: str
    amount: float
    currency: str
    due_date: str
    cost_center: str


# A tiny fixture standing in for the ERP replica.
_INVOICES = {
    "INV-4411": Invoice("INV-4411", "paid", 12450.00, "EUR", "2026-05-30", "CC-PROCUREMENT"),
    "INV-4388": Invoice("INV-4388", "overdue", 8200.00, "EUR", "2026-04-15", "CC-PROCUREMENT"),
    "INV-9001": Invoice("INV-9001", "pending", 40000.00, "USD", "2026-07-01", "CC-EXEC"),
}


class ErpClient:
    """The service-identity client. Note what it CANNOT do: no write methods
    exist, because the tools don't need them and the credential doesn't grant
    them. The first law, expressed as an absent method."""

    def get_invoice(self, invoice_id: str) -> Invoice | None:
        return _INVOICES.get(invoice_id)


erp = ErpClient()
