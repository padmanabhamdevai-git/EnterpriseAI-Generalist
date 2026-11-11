"""reranker.py — the funnel's careful stage (book 6.11.2).

Production options, in order of preference:
1. A hosted re-rank API (Cohere Rerank-class) — one call, strong quality.
2. A local cross-encoder (BGE-reranker-class via sentence-transformers) —
   keeps the private plane (Ch. 4) viable end to end.
3. This file's fallback: LLM-scored relevance. Slower and costlier per
   candidate than a true cross-encoder, but dependency-free for the labs
   and good enough to demonstrate the funnel's quality effect.

Swap implementations behind rerank() — the funnel shape is the contract.
"""
import json

from ai_client import ask


def rerank(question: str, hits: list[dict]) -> list[dict]:
    """Re-score candidates for actual relevance to the question; sort desc.

    One batched LLM call scores all candidates 0-10. For >30 candidates or
    latency-sensitive paths, use a real cross-encoder instead (see module
    docstring).
    """
    if len(hits) <= 1:
        return hits

    numbered = "\n\n".join(
        f"[{i}] {h['text'][:400]}" for i, h in enumerate(hits)
    )
    resp = ask(
        f"Score each passage 0-10 for how directly it answers the question.\n"
        f"Question: {question}\n\nPassages:\n{numbered}\n\n"
        f'Output ONLY JSON: {{"scores": [<one number per passage, in order>]}}',
        system="You are a precise relevance scorer. No prose.",
        provider="openai", max_tokens=1200,
    ).text

    try:
        text = resp.strip()
        if text.startswith("```"):
            text = text.split("```")[1].removeprefix("json").strip()
        scores = json.loads(text)["scores"]
        assert len(scores) == len(hits)
    except Exception:
        return hits          # fail open: fused order is a sane fallback

    for h, s in zip(hits, scores):
        h["score"] = float(s)
    return sorted(hits, key=lambda h: h["score"], reverse=True)
