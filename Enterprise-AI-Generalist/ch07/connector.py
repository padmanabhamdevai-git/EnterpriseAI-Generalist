"""connector.py — one interface, many sources (book 7.11.2).

A connector's four duties: enumerate changes, fetch content, extract ACLs,
and report freshness. Everything else is per-source configuration.

The filesystem reference implementation walks a directory tree, maps
subfolders to tiers, and uses mtimes as the change cursor — trivially
simple, and it exercises every duty a SharePoint connector must perform,
including deletion visibility.
"""
import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Protocol


@dataclass
class SourceDocument:
    id: str                      # stable ID in the source system
    title: str
    text: str                    # parsed content (parsing profile applied)
    version: str
    tiers: list[str]             # inherited from source ACLs, or owner-assigned
    domain: str
    deleted: bool = False        # deletion visibility is part of the contract
    metadata: dict = field(default_factory=dict)


class Connector(Protocol):
    """The contract every source connector implements.

    A connector review is four questions — changes? deletions? ACLs?
    freshness? — and any 'no' is a register entry the domain owner must see.
    """

    def changed_since(self, cursor: str | None) -> Iterator[SourceDocument]:
        """Yield documents changed since the cursor (None = full backfill).
        MUST include deletions (deleted=True) — a connector that can't see
        deletions can't honor erasure."""
        ...

    def freshness(self) -> datetime:
        """When did we last successfully observe the source? Feeds the SLA."""
        ...


class FilesystemConnector:
    """Reference implementation: folder tree → documents.

    Layout convention:  <root>/<tier>/<doc>.md   (subfolder = access tier)
    Cursor: JSON of {path: mtime} from the previous run — mtime deltas are
    changes; paths present in the cursor but missing on disk are deletions.
    """

    def __init__(self, root: str, domain: str):
        self.root = Path(root)
        self.domain = domain
        self._observed = datetime.now(timezone.utc)

    def _snapshot(self) -> dict[str, float]:
        return {str(p.relative_to(self.root)): p.stat().st_mtime
                for p in self.root.rglob("*.md")}

    def changed_since(self, cursor: str | None) -> Iterator[SourceDocument]:
        previous: dict[str, float] = json.loads(cursor) if cursor else {}
        current = self._snapshot()
        self._observed = datetime.now(timezone.utc)

        # Deletions first: in the cursor, gone from disk.
        for rel in sorted(set(previous) - set(current)):
            tier = rel.split(os.sep)[0]
            yield SourceDocument(
                id=f"{self.domain}/{rel}", title=Path(rel).stem, text="",
                version="deleted", tiers=[tier], domain=self.domain,
                deleted=True,
            )

        # New and changed:
        for rel, mtime in sorted(current.items()):
            if previous.get(rel) == mtime:
                continue                      # unchanged — costs nothing
            path = self.root / rel
            tier = rel.split(os.sep)[0]
            yield SourceDocument(
                id=f"{self.domain}/{rel}",
                title=path.stem.replace("-", " "),
                text=path.read_text(encoding="utf-8"),
                version=str(int(mtime)),
                tiers=[tier],
                domain=self.domain,
                metadata={"path": rel},
            )

    def cursor(self) -> str:
        """Serialize the current snapshot as the next run's cursor."""
        return json.dumps(self._snapshot())

    def freshness(self) -> datetime:
        return self._observed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="./sample_docs")
    ap.add_argument("--domain", default="hr")
    ap.add_argument("--cursor-file", default=".connector_cursor.json")
    args = ap.parse_args()

    conn = FilesystemConnector(args.source, args.domain)
    cursor_path = Path(args.cursor_file)
    cursor = cursor_path.read_text() if cursor_path.exists() else None

    changes = list(conn.changed_since(cursor))
    for doc in changes:
        flag = "DELETE" if doc.deleted else "UPSERT"
        print(f"{flag:>6}  {doc.id}  tiers={doc.tiers}  v={doc.version}")
    print(f"\n{len(changes)} change(s); freshness={conn.freshness().isoformat()}")

    cursor_path.write_text(conn.cursor())
    print(f"cursor written to {cursor_path} — run again to see idempotency")
