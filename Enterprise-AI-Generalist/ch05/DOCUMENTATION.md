# Chapter 5 — Documentation

Detailed developer documentation for the Chapter 5 code samples ("Why AI Needs
Your Data: RAG Concepts and Architecture"). Complements the short `README.md` with
setup, per-file walkthroughs, expected output, and reasoning-model notes.

---

## 1. What this chapter teaches

Chapter 5 introduces **Retrieval-Augmented Generation (RAG)** — the pattern of
grounding model answers in your own documents instead of model weights alone:

1. **Meaning as geometry** — embeddings turn text into vectors; similar meaning
   clusters together (`embeddings_explorer.py`).
2. **The seven-stage RAG pipeline** — ingest → chunk → embed → store → retrieve →
   augment → generate, in plain Python with no framework (`mini_rag.py`).
3. **Grounding beats hallucination** — same question answered three ways: ungrounded,
   grounded with citations, honest refusal when absent (`grounding_demo.py`).

Chapter 6 industrializes every line (pgvector, FastAPI service boundary).

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Modern type hints. |
| ch01 wrapper | `mini_rag.py` and `grounding_demo.py` import `ai_client`. |
| `numpy>=1.26.0` | Cosine similarity in embeddings and retrieval. |
| `openai` SDK | Embeddings API (`text-embedding-3-small`). |
| API keys | `OPENAI_API_KEY` (embeddings) and `ANTHROPIC_API_KEY` (generation). |

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

---

## 3. Setup

Make the ch01 wrapper importable:

```bash
# Windows PowerShell
$env:PYTHONPATH="..\ch01"
$env:PYTHONUTF8="1"
# macOS/Linux
export PYTHONPATH=../ch01
```

`embeddings_explorer.py` loads API keys from `../ch01/.env` directly.
`ai_client.py` also calls `load_dotenv()` when imported.

---

## 4. Files in this chapter

| File | Book section | Purpose |
|---|---|---|
| `embeddings_explorer.py` | 5.11.1 | Similarity matrix over enterprise sentences — meaning as geometry. |
| `corpus.py` | 5.11.2 | Three fictional Meridian policy documents, pre-chunked with metadata. |
| `mini_rag.py` | 5.11.2 | Canonical seven-stage RAG pipeline in ~100 lines with grounding contract. |
| `grounding_demo.py` | 5.11.3 | Same question three ways: ungrounded / grounded / honest refusal. |

### 4.1 `embeddings_explorer.py`
Embeds five sentences with `text-embedding-3-small` and prints the full cosine
similarity matrix. Key demonstration: s0 and s1 share meaning but almost no words
(similarity ~0.64), while s0 and s3 are different topics (similarity ~0.01).

### 4.2 `corpus.py`
12 pre-chunked policy excerpts from three documents (Travel & Expense, Sev-1
Runbook, Remote Work). Metadata on each chunk (`doc`, `version`, `section`) enables
citations and filtering. The Sev-1 runbook deliberately uses non-default details
(20-minute SLA, "Incident Conductor", chat-first bridge) so ungrounded answers can
be checked against the corpus.

### 4.3 `mini_rag.py`
The full pipeline:
1. **Embed** all chunks once (offline stage).
2. **Retrieve** top-k nearest chunks by cosine similarity.
3. **Augment** with a grounding contract ("answer ONLY from sources").
4. **Generate** via Anthropic with citations.

The vector "store" is a Python list on purpose — the contract is identical at scale.

### 4.4 `grounding_demo.py`
Runs the Sev-1 escalation question three ways to demonstrate why RAG matters. Also
tests an absent question (dogs in office) for honest refusal.

---

## 5. Reasoning-model changes

Adjustments for current flagship models:

1. **`temperature` removed** from `mini_rag.py` and `grounding_demo.py`.
2. **`max_tokens` raised** to 800 for generation calls (reasoning models need
   headroom for longer grounded answers).
3. **`embeddings_explorer.py`** — explicit `load_dotenv` path to `../ch01/.env`
   so embeddings work when run from the `ch05` directory without copying `.env`.

Note: modern reasoning models may refuse to fabricate when ungrounded (as observed
in a recent run) rather than inventing plausible-sounding facts. The grounded and
absent comparisons still demonstrate the core lesson: citations from your corpus
vs. honest refusal when sources don't cover the question.

---

## 6. How to run

```bash
python embeddings_explorer.py   # similarity matrix (~5s, 1 embedding API call)
python mini_rag.py              # 3 RAG questions (~20s, embed + 3 generation calls)
python grounding_demo.py        # ungrounded vs grounded vs absent (~20s)
```

> **Iron rule:** chunks and queries MUST use the same embedding model
> (`text-embedding-3-small`). Vectors from different models live in different
> geometries.

### Observed output (shape; exact values vary)

`embeddings_explorer.py`:

```
s0 vs s1 (same meaning, no shared words): 0.64
s0 vs s3 (different topics):              0.01
```

`mini_rag.py`:

```
Q: Can I book business class to Singapore?
A: ... [TE-Policy §5.2] ... [TE-Policy §4.1]

Q: What's the per-diem for Antarctica field work?
A: This isn't covered in the current policy documents.
```

`grounding_demo.py`:

```
2 · GROUNDED: ... [Sev1-Runbook §2.1] ... [Sev1-Runbook §3.1]
3 · ABSENT: This isn't covered in the current policy documents.
```

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: ai_client` | ch01 not importable | Set `PYTHONPATH=../ch01`. |
| `ModuleNotFoundError: numpy` | Dependency missing | `pip install -r requirements.txt`. |
| `AuthenticationError` on embeddings | Missing `OPENAI_API_KEY` | Verify `ch01/.env` has the key. |
| Poor retrieval scores | Query and chunks use different embedding models | Keep `EMBED_MODEL` pinned everywhere. |
| Ungrounded answer refuses instead of fabricating | Modern model safety/reasoning behavior | Grounded and absent demos still teach the lesson. |
| `UnicodeEncodeError` | Windows cp1252 console | `$env:PYTHONUTF8="1"`. |

---

## 8. Notes

- All companies, policies, and procedures are fictional.
- `chunker.py` (section 5.12 Cursor exercise) is left for the reader.
- Do not "fix" the Sev-1 runbook's deliberate non-default details — they power
  `grounding_demo.py`'s checkable contrast.
- Models used at time of writing: `text-embedding-3-small`, `claude-sonnet-5`.
