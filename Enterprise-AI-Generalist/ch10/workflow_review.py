"""workflow_review.py — a TIER-R readiness checker for n8n workflow exports (book 10.11.2).

Reads an exported workflow JSON and heuristically assesses the five
reliability properties. Like Chapter 8's capability_audit, it sorts a
review queue — a human confirms; this finds the obvious gaps fast.

Heuristic by design: it string-matches the exported JSON. A false PASS on a
cleverly-named node is expected, and the human review is the backstop.
"""
import json
import sys
from pathlib import Path


def _check(label: str, ok: bool, detail: str) -> None:
    print(f"  [{'PASS' if ok else 'GAP '}] {label:<18} {detail}")


def review(path: str) -> None:
    wf = json.loads(Path(path).read_text())
    nodes = wf.get("nodes", [])
    names = [n.get("name", "") for n in nodes]
    types = [n.get("type", "") for n in nodes]
    blob = json.dumps(wf).lower()

    print(f"Reviewing '{wf.get('name', path)}'  ({len(nodes)} nodes)\n")

    # T — Triggered reliably (n8n trigger node types vary: *Trigger, webhook,
    # cron, schedule, and the email/IMAP read triggers)
    triggers = [t for t in types if any(k in t.lower() for k in
                ("trigger", "webhook", "cron", "schedule", "emailread", "imap"))]
    _check("T - Triggered", bool(triggers),
           f"trigger node(s): {triggers}" if triggers else "NO trigger node found")

    # I — Idempotent
    idem = any(k in blob for k in ("idempot", "already processed", "dedupe",
                                   "message_id", "messageid", "seen_key"))
    _check("I - Idempotent", idem,
           "idempotency signal present" if idem
           else "no idempotency check - retries/dupes may double-act")

    # E — Error-handled
    err = any(k in blob for k in ("continueonfail", "erroroutput", "retryonfail",
                                  "error trigger", "deadletter", "dead_letter",
                                  "onerror", "maxtries"))
    _check("E - Error-handled", err,
           "error handling present" if err
           else "no retry/error-branch/dead-letter - first null crashes it")

    # R — Recoverable (proxied by idempotency + error handling)
    _check("R - Recoverable", idem and err,
           "idempotent + error-handled -> re-runnable"
           if idem and err else "not safely re-runnable (needs I and E)")

    # R — Reportable (observability)
    obs = any(k in blob for k in ("log", "metric", "notify", "alert", "slack",
                                  "emailsend", "sendemail"))
    _check("R - Reportable", obs,
           "logging/alerting node present" if obs
           else "no observable output - failures will be silent")

    # Write-to-system-of-record flag → governance
    writes = [n for n, t in zip(names, types)
              if any(w in (n + t).lower() for w in
                     ("create", "update", "insert", "send", "post", "write", "delete"))]
    if writes:
        print(f"\n  ! writes to systems of record: {writes}")
        print("    -> needs governance review + idempotency before production")


if __name__ == "__main__":
    review(sys.argv[1] if len(sys.argv) > 1
           else "workflows/returns_coordinator.json")
