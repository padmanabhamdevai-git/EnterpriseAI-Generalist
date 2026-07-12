"""mini_rag.py — the canonical pipeline, no framework (book 5.11.2).

Ingest → chunk (corpus.py provides both) → embed → store (a list!) →
retrieve → augment → generate. Small enough to see through; that is
the point. Chapter 6 industrializes every line.
"""
import numpy as np

from ai_client import ask
from corpus import CHUNKS  # [{text, doc, section, version}, ...]
from embeddings_explorer import embed  # same pinned model — the iron rule

# --- Stages 3–4: embed once, "store" in memory --------------------------------
print(f"Embedding {len(CHUNKS)} chunks (one-time, offline stage)...")
VECTORS = embed([c["text"] for c in CHUNKS])
UNIT = VECTORS / np.linalg.norm(VECTORS, axis=1, keepdims=True)


# --- Stage 5: retrieve ----------------------------------------------------------
def retrieve(question: str, k: int = 4) -> list[dict]:
    """Embed the query; return the k nearest chunks with scores."""
    q = embed([question])[0]
    q = q / np.linalg.norm(q)
    scores = UNIT @ q
    top = np.argsort(scores)[::-1][:k]
    return [{**CHUNKS[i], "score": float(scores[i])} for i in top]


# --- Stage 6: augment — the grounding contract ---------------------------------
GROUNDING_CONTRACT = (
    "You are Meridian Systems' policy assistant.\n"
    "Answer ONLY from the sources provided below.\n"
    "Cite every claim as [doc §section].\n"
    "If the sources do not contain the answer, reply exactly: "
    "\"This isn't covered in the current policy documents.\" and suggest "
    "contacting the document owner. Never answer from general knowledge."
)


def build_prompt(question: str, hits: list[dict]) -> str:
    sources = "\n\n".join(
        f"[{h['doc']} §{h['section']}] (v{h['version']}, score {h['score']:.2f})\n"
        f"{h['text']}"
        for h in hits
    )
    return f"SOURCES:\n{sources}\n\nQUESTION: {question}"


# --- Stage 7: generate ------------------------------------------------------------
def answer(question: str, k: int = 4) -> str:
    hits = retrieve(question, k)
    print("  retrieved:", [(h["doc"], h["section"], round(h["score"], 2))
                           for h in hits])
    return ask(build_prompt(question, hits), system=GROUNDING_CONTRACT,
               provider="anthropic", max_tokens=800).text


if __name__ == "__main__":
    for q in (
        "Can I book business class to Singapore?",
        "What's the escalation path for a Sev-1 outage?",
        "What's the per-diem for Antarctica field work?",  # absent → refusal
    ):
        print(f"\nQ: {q}")
        print(f"A: {answer(q)}")
