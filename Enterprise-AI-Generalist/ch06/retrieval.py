"""retrieval.py — hybrid search + RRF + re-rank (book 6.11.2).

The retrieval quality stack of §6.4.3 as a funnel:
hybrid (vector ∪ lexical, fused by rank) → 30 candidates → re-rank → top 5.

Permission filtering is a SQL predicate in BOTH CTEs — permissions have
no side door. Run `python retrieval.py --mode vector|lexical|hybrid "q"`
for the baseline comparisons of Exercise 2.
"""
import argparse
import os

import psycopg
from dotenv import load_dotenv

from embeddings import embed_one
from reranker import rerank

load_dotenv()
DB_URL = os.environ["DATABASE_URL"]

HYBRID_SQL = """
WITH vec AS (
    SELECT c.id, ROW_NUMBER() OVER (ORDER BY c.embedding <=> %(qvec)s::vector) AS r
    FROM chunks c JOIN documents d ON d.id = c.document_id
    WHERE d.access_tier = ANY(%(tiers)s)
    ORDER BY c.embedding <=> %(qvec)s::vector LIMIT 25
),
lex AS (
    SELECT c.id, ROW_NUMBER() OVER (
        ORDER BY ts_rank(c.lexical, websearch_to_tsquery('english', %(q)s)) DESC) AS r
    FROM chunks c JOIN documents d ON d.id = c.document_id
    WHERE c.lexical @@ websearch_to_tsquery('english', %(q)s)
      AND d.access_tier = ANY(%(tiers)s)
    LIMIT 25
)
SELECT c.id, c.document_id, c.section, c.text,
       COALESCE(1.0/(60 + vec.r), 0) + COALESCE(1.0/(60 + lex.r), 0) AS rrf
FROM chunks c
LEFT JOIN vec ON vec.id = c.id
LEFT JOIN lex ON lex.id = c.id
WHERE vec.id IS NOT NULL OR lex.id IS NOT NULL
ORDER BY rrf DESC
LIMIT %(candidates)s;
"""

VECTOR_ONLY_SQL = """
SELECT c.id, c.document_id, c.section, c.text,
       1 - (c.embedding <=> %(qvec)s::vector) AS score
FROM chunks c JOIN documents d ON d.id = c.document_id
WHERE d.access_tier = ANY(%(tiers)s)
ORDER BY c.embedding <=> %(qvec)s::vector
LIMIT %(candidates)s;
"""

LEXICAL_ONLY_SQL = """
SELECT c.id, c.document_id, c.section, c.text,
       ts_rank(c.lexical, websearch_to_tsquery('english', %(q)s)) AS score
FROM chunks c JOIN documents d ON d.id = c.document_id
WHERE c.lexical @@ websearch_to_tsquery('english', %(q)s)
  AND d.access_tier = ANY(%(tiers)s)
ORDER BY score DESC
LIMIT %(candidates)s;
"""


def _rows_to_hits(rows) -> list[dict]:
    return [{"id": r[0], "doc": r[1], "section": r[2], "text": r[3],
             "score": float(r[4])} for r in rows]


def retrieve(conn: psycopg.Connection, question: str, tiers: list[str],
             candidates: int = 30, k: int = 5, mode: str = "hybrid",
             use_reranker: bool = True) -> list[dict]:
    """Retrieve → (fuse) → re-rank → top k."""
    params = {"q": question, "tiers": tiers, "candidates": candidates,
              "qvec": str(embed_one(question))}
    sql = {"hybrid": HYBRID_SQL, "vector": VECTOR_ONLY_SQL,
           "lexical": LEXICAL_ONLY_SQL}[mode]
    hits = _rows_to_hits(conn.execute(sql, params).fetchall())
    if use_reranker and mode == "hybrid":
        hits = rerank(question, hits)
    return hits[:k]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--mode", choices=["vector", "lexical", "hybrid"],
                    default="hybrid")
    ap.add_argument("--no-rerank", action="store_true")
    args = ap.parse_args()

    with psycopg.connect(DB_URL) as conn:
        hits = retrieve(conn, args.question, tiers=["all-employees"],
                        mode=args.mode, use_reranker=not args.no_rerank)
        print(f"mode={args.mode}  rerank={not args.no_rerank}")
        for h in hits:
            print(f"  {h['score']:.3f}  [{h['doc']} §{h['section']}] "
                  f"{h['text'][:70]}...")
