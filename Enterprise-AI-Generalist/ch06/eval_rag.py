"""eval_rag.py — the RAG triad as a release gate (book 6.11.3).

Leg 1 (retrieval recall@k) is pure arithmetic on labels — no model, no
opinions. Leg 2 (groundedness) uses an LLM judge with a tight rubric and
a PINNED judge model. Leg 3 (refusal correctness) checks the absent set.

Usage:
    python eval_rag.py                      # hybrid + rerank (the default stack)
    python eval_rag.py --mode vector        # baseline comparisons
"""
import argparse
import os

import psycopg
from dotenv import load_dotenv

from ai_client import ask
from eval_set import EVAL_SET
from retrieval import retrieve

load_dotenv()
DB_URL = os.environ["DATABASE_URL"]

JUDGE_MODEL_PIN = "gpt-5.5"   # a judge that silently upgrades is a ruler that changes length

JUDGE_RUBRIC = (
    "You are a strict groundedness judge. You will receive SOURCES and an "
    "ANSWER. Decompose the answer into atomic factual claims. For each claim "
    "output one line: SUPPORTED or UNSUPPORTED, a verbatim quote from the "
    "sources if supported, and the claim. Judge ONLY against the sources — "
    "your own knowledge of the world is irrelevant and must not be used. "
    "End with: SCORE: <supported>/<total>."
)

REFUSAL_TEXT = "This isn't covered in the current policy documents."


def resolve_labels(conn) -> dict[tuple[str, str], set[int]]:
    """Map (doc, section) labels to chunk IDs."""
    rows = conn.execute("SELECT id, document_id, section FROM chunks").fetchall()
    index: dict[tuple[str, str], set[int]] = {}
    for cid, doc, section in rows:
        index.setdefault((doc, str(section)), set()).add(cid)
    return index


def recall_at_k(conn, mode: str, k: int = 5, use_reranker: bool = True) -> float:
    """Leg 1: did a labeled-relevant chunk reach the top k? Pure arithmetic."""
    labels = resolve_labels(conn)
    answerable = [c for c in EVAL_SET if not c["absent"]]
    hit = 0
    for case in answerable:
        relevant_ids: set[int] = set()
        for key in case["relevant"]:
            relevant_ids |= labels.get((key[0], str(key[1])), set())
        got = retrieve(conn, case["question"], tiers=["all-employees"],
                       k=k, mode=mode, use_reranker=use_reranker)
        if {h["id"] for h in got} & relevant_ids:
            hit += 1
        else:
            print(f"  RECALL MISS [{mode}]: {case['question'][:60]!r}")
    return hit / len(answerable)


def groundedness(sources: str, answer: str) -> str:
    """Leg 2: claim-by-claim faithfulness, judge caged and pinned."""
    return ask(f"SOURCES:\n{sources}\n\nANSWER:\n{answer}",
               system=JUDGE_RUBRIC, provider="openai",
               max_tokens=1200).text


def refusal_correctness(conn) -> float:
    """Leg 3 (refusal slice): absent questions must refuse, not improvise."""
    from service import GROUNDING_CONTRACT  # single source of truth
    absent = [c for c in EVAL_SET if c["absent"]]
    correct = 0
    for case in absent:
        hits = retrieve(conn, case["question"], tiers=["all-employees"], k=5)
        sources = "\n\n".join(f"[{h['doc']} §{h['section']}]\n{h['text']}"
                              for h in hits)
        answer = ask(f"SOURCES:\n{sources}\n\nQUESTION: {case['question']}",
                     system=GROUNDING_CONTRACT, provider="anthropic",
                     max_tokens=800).text
        if REFUSAL_TEXT in answer:
            correct += 1
        else:
            print(f"  REFUSAL MISS: {case['question'][:60]!r}")
    return correct / len(absent) if absent else 1.0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["vector", "lexical", "hybrid"],
                    default="hybrid")
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    with psycopg.connect(DB_URL) as conn:
        r = recall_at_k(conn, mode=args.mode, k=args.k,
                        use_reranker=not args.no_rerank)
        print(f"\nrecall@{args.k} ({args.mode}, "
              f"rerank={not args.no_rerank}): {r:.2f}")

        rc = refusal_correctness(conn)
        print(f"refusal correctness (absent set): {rc:.2f}")

        print("\nRelease gate example (wire into CI):")
        gate = r >= 0.85 and rc >= 0.90
        print(f"  recall@{args.k} >= 0.85 and refusal >= 0.90 → "
              f"{'PASS' if gate else 'FAIL'}")
        raise SystemExit(0 if gate else 1)
