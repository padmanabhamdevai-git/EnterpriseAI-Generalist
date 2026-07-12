"""embeddings.py — pinned embedding model, single + batch helpers (ch06).

The iron rule from Chapter 5: chunks and queries MUST use the same model.
Change EMBED_MODEL and you owe the corpus a full re-embed (and schema.sql
a matching VECTOR(n) dimension).
"""
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"   # pinned; 1536 dims — matches schema.sql
BATCH_SIZE = 256


def embed_one(text: str) -> list[float]:
    resp = _client.embeddings.create(model=EMBED_MODEL, input=[text])
    return resp.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batched embedding for ingestion. For large backfills, prefer the
    vendor's async batch endpoint (half price, relaxed latency — Ch. 2 §2.17)."""
    out: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        resp = _client.embeddings.create(model=EMBED_MODEL,
                                         input=texts[i:i + BATCH_SIZE])
        out.extend(d.embedding for d in resp.data)
    return out
