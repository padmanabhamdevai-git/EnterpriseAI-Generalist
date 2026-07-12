"""ai_client_async.py — Exercise 4 solution: concurrent multi-provider fan-out.

Extends ai_client.ask() with provider="both": query OpenAI and Anthropic
concurrently and compare token usage and latency side by side.

Uses a thread pool rather than native async SDK clients so that the
synchronous ask() from ai_client.py is reused unchanged — the simplest
thing that works, which is the point at this stage of the book.
"""
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ai_client import AIResponse, ask


@dataclass
class TimedResponse:
    """An AIResponse plus wall-clock latency in seconds."""

    response: AIResponse
    latency_s: float


def _timed_ask(prompt: str, system: str, provider: str, **kwargs) -> TimedResponse:
    start = time.perf_counter()
    resp = ask(prompt, system=system, provider=provider, **kwargs)
    return TimedResponse(response=resp, latency_s=time.perf_counter() - start)


def ask_both(prompt: str, system: str = "", **kwargs) -> list[TimedResponse]:
    """Query both providers concurrently; return results as they were requested."""
    providers = ("openai", "anthropic")
    with ThreadPoolExecutor(max_workers=len(providers)) as pool:
        futures = [
            pool.submit(_timed_ask, prompt, system, provider, **kwargs)
            for provider in providers
        ]
        return [f.result() for f in futures]


if __name__ == "__main__":
    QUESTION = (
        "List three risks of connecting an AI agent directly "
        "to a production ERP system."
    )
    results = ask_both(QUESTION)

    print(f"{'provider':<12}{'latency':>10}{'in tok':>8}{'out tok':>9}")
    for t in results:
        r = t.response
        print(
            f"{r.provider:<12}{t.latency_s:>9.2f}s"
            f"{r.input_tokens:>8}{r.output_tokens:>9}"
        )

    for t in results:
        print(f"\n=== {t.response.provider} ===\n{t.response.text}")
