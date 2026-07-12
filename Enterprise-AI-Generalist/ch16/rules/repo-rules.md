# Repository rules (Layer 2) — this repo's conventions
<!-- Owned by the team. Sharpened within the hour of every repeated agent mistake.
     Example instantiation for a Meridian estate service; edit for your repo.
     Chapter 16, section 16.5.2. -->

## Architecture
- Services follow the ch09 pattern: authentication in `auth.py`; every tool/handler
  takes a `Caller` and enforces its own limits — the caller's story never overrides
  the tool's rules (the first law).
- Model calls go through the enterprise gateway client (`gateway.py`) — never a
  vendor SDK called directly with a raw key.
- Retrieval delegates to the knowledge-platform API. Do NOT embed retrieval logic
  (chunking, vector search) in services — that lives in the platform (ch07).

## Stack and idioms
- Python 3.11+, type hints on public functions, dataclasses over dicts for
  structured state.
- Errors: raise specific exceptions with actionable messages. `except: pass`
  never merges.
- Configuration via environment variables read in ONE module (`config.py`).

## Tests
- pytest; one test file per module; every bug fix adds the test that would have
  caught it.
- Tests assert MESSAGES and BEHAVIOR, not just types. A test without a meaningful
  assertion is coverage theater and will be rejected in review.
- The eval suite (`eval_*.py`) is a release gate: it runs in CI and blocks merge.

## Frozen zones
- `/legacy` is frozen: read for context, never modify.
- Database migrations only via `make migrate` — never hand-edit migration files.

## Vocabulary
- "door" = a governed MCP/API server (ch09). "the island" = prototype sandbox (ch15).
- "slice" = one reviewable unit of work: one behavior + its tests, small enough
  to review in one sitting.
