"""ingest.py — the pipeline: chunk → embed → upsert, incrementally (book 6.11.1).

Production behaviors demonstrated:
- idempotency via content hashing (re-runs are free)
- atomic replace-not-append (readers never see a half-updated document)
- deletion that provably cascades to vectors (run the erasure drill)

Usage:
    python ingest.py --init           # apply schema.sql, then ingest ch05 corpus
    python ingest.py                  # ingest/refresh ch05 corpus
    python ingest.py --delete DOC_ID  # the erasure drill
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from embeddings import embed_batch

load_dotenv()
DB_URL = os.environ["DATABASE_URL"]

# Reuse Chapter 5's corpus as the seed dataset (see README for path setup).
sys.path.insert(0, str(Path(__file__).parent.parent / "ch05"))
from corpus import CHUNKS as CH05_CHUNKS  # noqa: E402


def documents_from_ch05() -> list[tuple[dict, list[dict]]]:
    """Group Chapter 5's flat chunk list into (document, chunks) pairs."""
    docs: dict[str, list[dict]] = {}
    for c in CH05_CHUNKS:
        docs.setdefault(c["doc"], []).append(c)
    out = []
    for doc_id, chunks in docs.items():
        meta = chunks[0]
        out.append((
            {"id": doc_id, "title": doc_id.replace("-", " "),
             "source": "ch05-corpus", "version": meta["version"]},
            [{"section": c["section"], "text": c["text"], "metadata": "{}"}
             for c in chunks],
        ))
    return out


def upsert_document(conn: psycopg.Connection, doc: dict, chunks: list[dict]) -> str:
    """Insert/update one document and its chunks atomically.
    Returns: 'skipped' (unchanged), 'updated', or 'inserted'."""
    content_hash = hashlib.sha256(
        "".join(c["text"] for c in chunks).encode()
    ).hexdigest()

    with conn.transaction():
        row = conn.execute(
            "SELECT content_hash FROM documents WHERE id = %s", (doc["id"],)
        ).fetchone()

        if row and row[0] == content_hash:
            return "skipped"                 # idempotency: re-runs are free

        # Replace-not-append: the old version's chunks must not survive.
        conn.execute("DELETE FROM chunks WHERE document_id = %s", (doc["id"],))
        conn.execute(
            """INSERT INTO documents (id, title, source, version, content_hash, access_tier)
               VALUES (%(id)s, %(title)s, %(source)s, %(version)s, %(hash)s, %(tier)s)
               ON CONFLICT (id) DO UPDATE SET
                 title = EXCLUDED.title, version = EXCLUDED.version,
                 content_hash = EXCLUDED.content_hash,
                 access_tier = EXCLUDED.access_tier, ingested_at = now()""",
            {**doc, "hash": content_hash, "tier": doc.get("tier", "all-employees")},
        )

        vectors = embed_batch([c["text"] for c in chunks])   # one batched call
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO chunks (document_id, section, text, embedding, metadata)
                   VALUES (%s, %s, %s, %s::vector, %s)""",
                [(doc["id"], c["section"], c["text"], str(v),
                  c.get("metadata", "{}"))
                 for c, v in zip(chunks, vectors)],
            )
    return "updated" if row else "inserted"


def delete_document(conn: psycopg.Connection, doc_id: str) -> int:
    """Erasure that erases. CASCADE removes chunks — and with them, vectors."""
    with conn.transaction():
        deleted = conn.execute(
            "DELETE FROM documents WHERE id = %s RETURNING id", (doc_id,)
        ).fetchone()
    return 1 if deleted else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true", help="apply schema.sql first")
    ap.add_argument("--delete", metavar="DOC_ID", help="run the erasure drill")
    args = ap.parse_args()

    with psycopg.connect(DB_URL) as conn:
        # pgvector adapter: send Python lists as vector literals
        conn.execute("SET search_path TO public")

        if args.init:
            conn.execute(Path(__file__).with_name("schema.sql").read_text())
            conn.commit()
            print("schema applied")

        if args.delete:
            n = delete_document(conn, args.delete)
            left = conn.execute(
                "SELECT count(*) FROM chunks WHERE document_id = %s",
                (args.delete,)).fetchone()[0]
            print(f"deleted={n}; chunks remaining for {args.delete}: {left}")
            sys.exit(0)

        for doc, chunks in documents_from_ch05():
            result = upsert_document(conn, doc, chunks)
            print(f"{result:>8}  {doc['id']}  ({len(chunks)} chunks)")
        conn.commit()
        total = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
        print(f"\ntotal chunks in store: {total}")
