# Chapter 6 — Building Production RAG Systems

The Enterprise RAG Reference Architecture as a small, complete, runnable
service: FastAPI + PostgreSQL/pgvector + hybrid search + re-ranking +
the RAG-triad evaluation harness.

| File | Book section | Purpose |
|---|---|---|
| `docker-compose.yml` | 6.10 | Local Postgres with pgvector, one command |
| `schema.sql` | 6.9 | documents + chunks tables; HNSW + GIN indexes; CASCADE deletion |
| `embeddings.py` | — | Pinned embedding model, single + batch helpers |
| `ingest.py` | 6.11.1 | Incremental, idempotent, versioned ingestion with real deletion |
| `retrieval.py` | 6.11.2 | Hybrid (vector + lexical) + RRF + re-rank funnel; `--mode` baselines |
| `reranker.py` | 6.11.2 | Re-ranking stage (LLM-scored fallback; swap in a cross-encoder) |
| `service.py` | 6.10 | FastAPI: /ask, /ingest, /health — citation verification, structured refusals |
| `eval_set.py` | 6.11.3 | Labeled questions over the ch05 corpus (answerable + absent) |
| `eval_rag.py` | 6.11.3 | recall@k (pure arithmetic) + groundedness judge (rubric-caged, pinned) |

## Quick start

```bash
cd ch06
cp ../ch01/.env .
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5433/rag" >> .env
cp ../ch01/ai_client.py .            # or export PYTHONPATH=../ch01

docker compose up -d                 # Postgres 16 + pgvector on :5433
python ingest.py --init              # applies schema.sql, ingests ch05 corpus
uvicorn service:app --reload

curl -s -X POST localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Can I book business class to Singapore?","user_tier":"all-employees"}' | jq

python eval_rag.py                   # the triad, with baselines per mode
```

No Docker? Create a free Supabase project (pgvector is pre-enabled), set
`DATABASE_URL` to its connection string, and everything else is identical.

## Design decisions (explained in the book)

- One Postgres carries all four indexes: text, vector (pgvector/HNSW),
  lexical (tsvector/GIN), metadata (JSONB). Hybrid search is one SQL query.
- `ON DELETE CASCADE` makes erasure real: deleting a document provably
  removes its chunks and vectors. Run the drill (Exercise 5).
- Permission filtering is a SQL predicate in BOTH hybrid CTEs — never a
  prompt instruction. The README's RLS section shows the row-level-security
  variant for multi-tenant deployments.
- The groundedness judge is pinned and its rubric forbids world knowledge:
  it scores SUPPORT, not truth.

## Row-level security variant (Lab 3)

```sql
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY chunk_tier_read ON chunks FOR SELECT
  USING (EXISTS (SELECT 1 FROM documents d
                 WHERE d.id = document_id
                   AND d.access_tier = ANY(current_setting('app.user_tiers')::text[]));
-- the service sets: SET app.user_tiers = '{all-employees,support}';
```

Models used at time of writing: `text-embedding-3-small` (1536 dims —
schema.sql's VECTOR(1536) must match your embedding model),
`gpt-5.5` (judge, pinned), `claude-sonnet-5` (generation).
All companies and documents are fictional.
