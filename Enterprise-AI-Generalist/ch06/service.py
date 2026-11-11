"""service.py — the service boundary (book 6.10).

FastAPI endpoints:
  POST /ask     — grounded answer with citations, structured status
  POST /ingest  — trigger re-ingestion of the seed corpus
  GET  /health  — liveness + store stats

Production behaviors demonstrated:
- typed request/response schemas (Ch. 4's contracts at the HTTP layer)
- permission tiers resolved at the boundary, enforced in SQL
- mechanical citation verification; unverifiable citations flag the response
- refusal as a structured outcome, not a string
"""
import os
import re

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from ai_client import ask
from retrieval import retrieve

load_dotenv()
DB_URL = os.environ["DATABASE_URL"]

app = FastAPI(title="Meridian Knowledge Service", version="1.0.0")

REFUSAL_TEXT = "This isn't covered in the current policy documents."

GROUNDING_CONTRACT = (
    "You are Meridian Systems' knowledge assistant.\n"
    "Answer ONLY from the sources provided below.\n"
    "Cite every claim as [doc §section].\n"
    f'If the sources do not contain the answer, reply exactly: "{REFUSAL_TEXT}" '
    "and suggest contacting the document owner. Never answer from general "
    "knowledge."
)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    user_tier: str = "all-employees"
    k: int = Field(default=5, ge=1, le=10)


class Citation(BaseModel):
    doc: str
    section: str


class AskResponse(BaseModel):
    status: str                    # answered | refused | flagged
    answer: str
    citations: list[Citation]
    unverified_citations: list[str]
    retrieved: list[dict]          # provenance: ids, sections, scores
    versions: dict                 # the release-record fields that matter here


CITATION_RE = re.compile(r"\[([\w-]+) §([\w.\-]+)\]")


def verify_citations(answer: str, hits: list[dict]) -> tuple[list[Citation], list[str]]:
    """Mechanical check: every [doc §section] in the answer must correspond
    to a retrieved chunk. Unverifiable citations flag the response —
    a rising flag rate is grounding drift's earliest smoke (§6.5.2)."""
    available = {(h["doc"], str(h["section"])) for h in hits}
    verified, unverified = [], []
    for doc, section in set(CITATION_RE.findall(answer)):
        if (doc, section) in available:
            verified.append(Citation(doc=doc, section=section))
        else:
            unverified.append(f"[{doc} §{section}]")
    return verified, unverified


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(req: AskRequest) -> AskResponse:
    with psycopg.connect(DB_URL) as conn:
        hits = retrieve(conn, req.question, tiers=[req.user_tier], k=req.k)

    sources = "\n\n".join(
        f"[{h['doc']} §{h['section']}]\n{h['text']}" for h in hits
    )
    answer = ask(f"SOURCES:\n{sources}\n\nQUESTION: {req.question}",
                 system=GROUNDING_CONTRACT, provider="anthropic",
                 max_tokens=800).text

    refused = REFUSAL_TEXT in answer
    citations, unverified = verify_citations(answer, hits)

    status = "refused" if refused else ("flagged" if unverified else "answered")
    return AskResponse(
        status=status,
        answer=answer,
        citations=citations,
        unverified_citations=unverified,
        retrieved=[{"id": h["id"], "doc": h["doc"], "section": h["section"],
                    "score": round(h["score"], 3)} for h in hits],
        versions={"embedding_model": "text-embedding-3-small",
                  "generation_model": "claude-sonnet-5",
                  "grounding_contract": "meridian/knowledge@1.0.0"},
    )


@app.get("/health")
def health() -> dict:
    with psycopg.connect(DB_URL) as conn:
        docs = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
        chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    return {"status": "ok", "documents": docs, "chunks": chunks}
