# Chapter 5 — Why AI Needs Your Data: RAG Concepts and Architecture

Code for sections 5.10–5.11 of the book: the complete RAG pipeline in plain
Python — no framework, no vector database. Small enough to see through;
that is the point. Chapter 6 industrializes every line.

| File | Book section | Purpose |
|---|---|---|
| `embeddings_explorer.py` | 5.11.1 | Meaning as geometry: similarity matrix over enterprise sentences |
| `corpus.py` | 5.11.2 | Three fictional Meridian policy documents, pre-chunked with metadata |
| `mini_rag.py` | 5.11.2 | The canonical seven stages in ~100 lines, with grounding contract |
| `grounding_demo.py` | 5.11.3 | Same question three ways: ungrounded / grounded / honest refusal |
| `chunker.py` | 5.12 (Cursor exercise) | Left for the reader; reference solution may be added under `solutions/` |

## Setup

```bash
cd ch05
cp ../ch01/.env .
cp ../ch01/ai_client.py .        # or export PYTHONPATH=../ch01
pip install -r ../requirements.txt   # numpy added for this chapter

python embeddings_explorer.py
python mini_rag.py
python grounding_demo.py
```

## Notes

- The embedding model is pinned (`text-embedding-3-small`): chunks and
  queries MUST use the same model — vectors from different models live in
  different geometries.
- `corpus.py` contains a Sev-1 escalation runbook whose details deliberately
  differ from any plausible default — that trap is what makes
  `grounding_demo.py`'s ungrounded answer checkably wrong. Don't "fix" it.
- The vector "store" is a Python list on purpose. The contract (nearest-k,
  filtered) is identical at every scale; Chapter 6 swaps in pgvector.

Models used at time of writing: `text-embedding-3-small`, `claude-sonnet-5`.
All companies, policies, and procedures are fictional.
