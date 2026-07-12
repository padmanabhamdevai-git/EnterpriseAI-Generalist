"""audit.py — the invocation audit log (book §9.19).

The log answers both the review board ('show me it can't over-read') and
the subpoena ('who did this, when'). It logs the HUMAN's identity, not the
service account — a log that records the service account survives review
and fails the subpoena.

Both allow AND deny are logged; a denied request is exactly what the audit
trail needs most.

PRODUCTION: emit to a durable, tamper-resistant, access-controlled pipeline
(SIEM / append-only store), fire-and-forget so the write never blocks the
response. Here we append structured lines to stdout and an in-memory buffer
so client_test.py can assert on them.
"""
from __future__ import annotations

import json
import time
from typing import Any

from auth import Caller

_BUFFER: list[dict] = []   # test-visible; production writes to the pipeline


def audit_log(caller: Caller, tool: str, args: dict[str, Any], *,
              decision: str, reason: str = "", result_summary: str = "") -> None:
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "identity": caller.subject,        # THE HUMAN — not the service account
        "host": caller.host,
        "tool": tool,
        "args": args,
        "decision": decision,              # allow | deny
        "reason": reason,
        "result": result_summary,
    }
    _BUFFER.append(entry)
    print("AUDIT " + json.dumps(entry))


def gateway_log(caller: Caller, server: str, tool: str, args: dict | None = None,
                *, decision: str, reason: str = "") -> None:
    """Gateway-layer log: the connection decision (defense-in-depth vs. the
    server's semantic log)."""
    entry = {"layer": "gateway", "identity": caller.subject, "host": caller.host,
             "server": server, "tool": tool, "decision": decision, "reason": reason}
    _BUFFER.append(entry)
    print("GATEWAY " + json.dumps(entry))


def recent(n: int = 20) -> list[dict]:
    return _BUFFER[-n:]
