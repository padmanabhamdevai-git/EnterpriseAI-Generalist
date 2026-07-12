-- Chapter 7 — tenancy enforced by the engine (book §7.11.1).
-- Visibility is a property of the database, not of application discipline.

-- Domain column: which knowledge domain a document belongs to.
ALTER TABLE documents ADD COLUMN IF NOT EXISTS domain TEXT NOT NULL DEFAULT 'support';

-- Denormalize tier + domain onto chunks at publish time for a join-free
-- hot path (see book §7.17). ch06's ingest is updated by ch07's connector
-- to populate these.
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS access_tier TEXT;
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS domain TEXT;

UPDATE chunks c SET access_tier = d.access_tier, domain = d.domain
FROM documents d WHERE d.id = c.document_id AND c.access_tier IS NULL;

CREATE INDEX IF NOT EXISTS chunks_tier_domain ON chunks (access_tier, domain);

-- Enable RLS. The service role must NOT bypass it.
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;

-- The one policy that matters: a chunk is visible iff the session's
-- resolved tiers include the chunk's tier. Every query path — /ask,
-- /search, the debug endpoint someone will add — inherits this.
DROP POLICY IF EXISTS chunk_visibility ON chunks;
CREATE POLICY chunk_visibility ON chunks FOR SELECT USING (
    access_tier = ANY (
        string_to_array(current_setting('app.tiers', true), ',')
    )
);

-- Ingestion path needs writes regardless of tiers (it runs as a separate
-- role); the API role gets SELECT only.
--   CREATE ROLE knowledge_api LOGIN PASSWORD '...' NOBYPASSRLS;
--   GRANT SELECT ON chunks, documents TO knowledge_api;
--   CREATE ROLE knowledge_ingest LOGIN PASSWORD '...' NOBYPASSRLS;
--   GRANT SELECT, INSERT, UPDATE, DELETE ON chunks, documents TO knowledge_ingest;
--   ALTER TABLE chunks FORCE ROW LEVEL SECURITY;  -- applies even to table owner

-- Leakage-test helper: run a probe under a given tier set.
--   BEGIN;
--   SELECT set_config('app.tiers', 'all-employees', true);  -- txn-scoped
--   SELECT count(*) FROM chunks WHERE access_tier = 'hr-only';  -- must be 0
--   COMMIT;
