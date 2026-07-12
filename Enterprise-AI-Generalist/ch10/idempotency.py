"""idempotency.py — the pattern that prevents double-acting (book 10.11.1).

Any workflow that writes to a system of record, sends a communication, or
moves money needs this. Retries and duplicate triggers are the NORMAL
operating condition, not an edge case — a non-idempotent workflow is
already wrong; it just hasn't been caught yet.
"""
import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

STATE_DB = Path(__file__).parent / "idempotency_state.db"


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB)
    conn.execute("CREATE TABLE IF NOT EXISTS processed "
                 "(key TEXT PRIMARY KEY, at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    return conn


def idempotency_key(*parts: str) -> str:
    """Stable key from the input. Same input -> same key, always.
    Use the most stable identifier available: a message ID, an order
    number, or a hash of the canonical payload."""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def claim(key: str) -> bool:
    """Atomically claim a key. Returns True if this is the FIRST time we've
    seen it (proceed), False if already processed (skip).

    The durable, atomic check is the whole point: an in-memory set doesn't
    survive a restart, and a check-then-write race double-acts under
    concurrency. The DB's unique constraint does check-and-set in one op.
    """
    with closing(_db()) as conn, conn:
        try:
            conn.execute("INSERT INTO processed (key) VALUES (?)", (key,))
            return True          # we claimed it first — proceed
        except sqlite3.IntegrityError:
            return False         # already processed — skip


def process_shipment_email(message_id: str, order_id: str, tracking: str) -> str:
    """A workflow step, made idempotent. The claim happens BEFORE any
    side effect, so a retry after a partial failure re-claims (False) and
    skips the already-done work."""
    key = idempotency_key("shipment", message_id, order_id)
    if not claim(key):
        return f"SKIP (already processed key={key[:8]})"
    # --- side effects go here: write tracking, update CRM, send email ---
    return f"PROCESSED order={order_id} tracking={tracking} key={key[:8]}"


if __name__ == "__main__":
    STATE_DB.unlink(missing_ok=True)   # fresh demo
    # Simulate the retry scenario from §10.5.2: the same email delivered twice.
    print(process_shipment_email("msg-4471", "ORD-8891", "1Z-TRACK-001"))
    print(process_shipment_email("msg-4471", "ORD-8891", "1Z-TRACK-001"))  # retry
    print(process_shipment_email("msg-4472", "ORD-8892", "1Z-TRACK-002"))  # new
    STATE_DB.unlink(missing_ok=True)   # clean up the demo db
