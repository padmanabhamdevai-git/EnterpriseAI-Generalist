"""unified_trace.py — one correlation ID, one timeline, four signals
(Chapter 20, sections 20.6.1, 20.12.1).

The answer to "observability is plural": a single correlated timeline that
follows a request across every blueprint layer, from which the four signal
classes (operational, quality, cost, safety) are derived.

Runs standalone: no API keys.

    python unified_trace.py
"""
from dataclasses import dataclass, field

# rough token prices per million (illustrative — verify current rates)
PRICE_PER_MTOK = {"frontier": 5.00, "fast": 0.50}


@dataclass
class Span:
    layer: str            # experience | agent | integration | knowledge | model
    op: str
    latency_ms: int
    tokens_in: int = 0
    tokens_out: int = 0
    model_tier: str = ""  # "frontier" | "fast" | "" (non-model hop)
    identity: str = ""
    guardrails: list[str] = field(default_factory=list)  # e.g. ["injection:pass", "grounding:0.91"]
    eval_score: float | None = None
    note: str = ""


@dataclass
class Trace:
    correlation_id: str          # minted at the experience layer, carried through every hop
    spans: list[Span] = field(default_factory=list)

    def total_latency_ms(self) -> int:
        return sum(s.latency_ms for s in self.spans)

    def total_tokens(self) -> int:
        return sum(s.tokens_in + s.tokens_out for s in self.spans)

    def cost_usd(self) -> float:
        c = 0.0
        for s in self.spans:
            if s.model_tier in PRICE_PER_MTOK:
                c += (s.tokens_in + s.tokens_out) / 1_000_000 * PRICE_PER_MTOK[s.model_tier]
        return round(c, 5)

    def signals(self) -> dict:
        """Derive the four signal classes from one trace."""
        trips = [g for s in self.spans for g in s.guardrails if g.endswith(":fail")]
        quality = [s.eval_score for s in self.spans if s.eval_score is not None]
        return {
            "operational": {"total_latency_ms": self.total_latency_ms(), "hops": len(self.spans)},
            "quality":     {"eval_scores": quality, "min_score": min(quality) if quality else None},
            "cost":        {"total_tokens": self.total_tokens(), "cost_usd": self.cost_usd()},
            "safety":      {"guardrail_trips": trips, "clean": not trips},
        }

    def timeline(self) -> None:
        print(f"TRACE {self.correlation_id}")
        for s in self.spans:
            extra = []
            if s.tokens_in or s.tokens_out:
                extra.append(f"{s.tokens_in}+{s.tokens_out}tok/{s.model_tier or '-'}")
            if s.guardrails:
                extra.append(" ".join(s.guardrails))
            if s.eval_score is not None:
                extra.append(f"eval={s.eval_score}")
            print(f"  [{s.latency_ms:>4}ms] {s.layer:<12} {s.op:<26} {'  '.join(extra)}")


# Mira's RMA call (Ch. 14), as one unified trace across the layers.
MIRA_CALL = Trace("rma-call-7f3a2c", [
    Span("experience", "voice turn (STT+TTS)", 620, identity="caller:+1-555-unverified"),
    Span("agent", "Mira decides: status lookup", 240, tokens_in=1800, tokens_out=90,
         model_tier="fast", guardrails=["injection:pass"], note="RFQ content treated as data"),
    Span("integration", "rma_status door (read-only)", 180, identity="human->app->ERP",
         guardrails=["scope:territory-ok"]),
    Span("knowledge", "FAQ retrieval (public tier)", 90, eval_score=0.94,
         guardrails=["grounding:0.94"]),
    Span("agent", "compose reply (2 sentences)", 210, tokens_in=1200, tokens_out=60,
         model_tier="fast", eval_score=0.91),
    Span("experience", "TTS + confirm readback", 300),
])


if __name__ == "__main__":
    print("THE UNIFIED TRACE (section 20.6.1) — one correlation ID, one timeline\n")
    MIRA_CALL.timeline()
    print("\nFOUR SIGNAL CLASSES, derived from the one trace:")
    for cls, data in MIRA_CALL.signals().items():
        print(f"  {cls:<12} {data}")
    print("\nThe three that don't throw errors — quality, cost, safety — are where")
    print("systems fail silently. An estate monitored only operationally looks healthy")
    print("while it degrades. The unified trace makes all four visible from one story.")
