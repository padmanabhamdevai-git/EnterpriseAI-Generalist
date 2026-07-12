"""placement.py — the three placement rules: data gravity, latency class,
egress economics (Chapter 18, sections 18.7.2, 18.11.2).

Where each component physically runs, decided by three rules IN ORDER.
Four representative workloads, walked through the rules — including the one
that surprises review boards: the analytics copilot lands beside the data
platform even against the "AI cloud" default.

Runs standalone: no API keys.

    python placement.py
"""
from dataclasses import dataclass

LATENCY_CLASSES = {          # Rule 2: the radius each interaction class permits
    "conversational-voice": "same-region co-location (experience + agent + model)",
    "interactive-chat":     "one region hop tolerable",
    "workflow-step":        "cross-cloud tolerable",
    "batch":                "wherever cheapest",
}


@dataclass
class Workload:
    name: str
    data_home: str            # Rule 1: where the data it consumes lives
    latency_class: str        # Rule 2: its most demanding consumer
    chatty_pairs: list[str]   # Rule 3: the high-volume component pairs
    default_instinct: str     # what the room assumes before the rules run
    ruled_placement: str      # where the rules actually put it
    note: str = ""


WORKLOADS = [
    Workload(
        name="Voice line (Mira)",
        data_home="order records via doors (cloud A, near ERP interconnect)",
        latency_class="conversational-voice",
        chatty_pairs=["STT<->LLM", "LLM<->TTS"],
        default_instinct="wherever the voice platform runs",
        ruled_placement="voice platform region co-located with model gateway region (cloud A)",
        note="Rule 2 dominates: the Turn Budget (Ch. 14) leaves no room for a region hop "
             "in the STT->LLM->TTS relay; the door call is one hop and masked by the filler line.",
    ),
    Workload(
        name="Knowledge platform",
        data_home="document estate + entitlement source (IdP) — cloud A",
        latency_class="interactive-chat",
        chatty_pairs=["retrieval<->model gateway"],
        default_instinct="'the AI cloud'",
        ruled_placement="cloud A, same region as the model gateway",
        note="Rule 1 anchors it to the documents; Rule 3 seals it: retrieval<->model is "
             "the chattiest pair in the estate — tokens of context per call, forever.",
    ),
    Workload(
        name="Media batch pipeline",
        data_home="DAM (cloud B) + brand references",
        latency_class="batch",
        chatty_pairs=["generation<->DAM ingestion"],
        default_instinct="same cloud as everything else",
        ruled_placement="wherever generation is cheapest this quarter; results ship to the DAM",
        note="Rule 2 frees it (batch = wherever cheapest); Rule 3 is satisfied because "
             "RESULTS cross clouds (small, valuable), not streams.",
    ),
    Workload(
        name="Analytics copilot",
        data_home="data platform / warehouse (cloud C)",
        latency_class="interactive-chat",
        chatty_pairs=["query results<->model context"],
        default_instinct="'all our AI is on cloud A'",
        ruled_placement="cloud C, beside the warehouse",
        note="THE surprise: Rule 1 overrides the AI-cloud default. A copilot streaming "
             "warehouse rows cross-cloud per query is an egress subscription with a chat "
             "interface. Price the standing stream annually and the argument ends.",
    ),
]


def place(w: Workload) -> None:
    print("=" * 76)
    print(f"WORKLOAD: {w.name}")
    print(f"  room's instinct: {w.default_instinct}")
    print(f"  Rule 1 (gravity): data lives at {w.data_home} -> anchor near it")
    print(f"  Rule 2 (latency): {w.latency_class} -> {LATENCY_CLASSES[w.latency_class]}")
    print(f"  Rule 3 (egress):  keep {', '.join(w.chatty_pairs)} within one cloud; "
          f"let results cross, not streams")
    print(f"  => PLACEMENT: {w.ruled_placement}")
    print(f"     {w.note}")
    print()


if __name__ == "__main__":
    print("THE THREE PLACEMENT RULES (section 18.7.2) — in order:")
    print("  1. Data gravity wins — compute moves to data")
    print("  2. Latency classes set the radius")
    print("  3. Egress economics decide the ties\n")
    for w in WORKLOADS:
        place(w)
    print("Network corollary (18.7.3): design the paths FIRST — private endpoints,")
    print("interconnects, and the VPN to on-premises systems have procurement lead")
    print("times; 'the model can't reach the ERP' in week ten resets the program.")
