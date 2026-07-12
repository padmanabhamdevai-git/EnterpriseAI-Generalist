-- Chapter 6 — the schema IS the system (book §6.9).
-- One Postgres database, four indexes: text, vector, lexical, metadata.

CREATE EXTENSION IF NOT EXISTS vector;

-- documents: one row per source document — the unit of versioning & deletion
CREATE TABLE IF NOT EXISTS documents (
    id           TEXT PRIMARY KEY,          -- stable source ID (wiki page ID, path)
    title        TEXT NOT NULL,
    source       TEXT NOT NULL,             -- register key: which system of truth
    version      TEXT NOT NULL,
    content_hash TEXT NOT NULL,             -- idempotency: skip unchanged docs
    access_tier  TEXT NOT NULL DEFAULT 'all-employees',
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- chunks: the retrieval unit — text + all four indexes in one row
CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    section     TEXT,                        -- for citations: [doc §section]
    text        TEXT NOT NULL,
    embedding   VECTOR(1536) NOT NULL,       -- dimension = pinned embedding model
    lexical     TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
    metadata    JSONB NOT NULL DEFAULT '{}'
);

-- The entire "vector database":
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_lexical_gin
    ON chunks USING gin (lexical);
CREATE INDEX IF NOT EXISTS chunks_document_id
    ON chunks (document_id);
