"""profiles.py — Meridian's three task profiles and candidate scores (Chapter 13, section 13.9).

The profiles, weights, and evidence strings here are the chapter's worked example,
expressed as data so a review board can diff them. Candidate names are kept
GENERIC ON PURPOSE ("incumbent workflow engine", "AI-native no-code platform",
"agent studio") — the method outlives any vendor list. Map them to the real
candidates in your own selection.

Score values are illustrative composites consistent with the chapter's narrative;
in a real selection every evidence string links to a pilot result, a document,
or a measurement.
"""
from scorecard import Candidate, Score, TaskProfile

# ---------------------------------------------------------------------------
# Profile W — the workhorse: ~60 deterministic + AI-infused workflows touching
# ERP/CRM through governed doors. Built by the automation team.
# ---------------------------------------------------------------------------
PROFILE_W = TaskProfile(
    name="W (workhorse)",
    description="Governed enterprise workflows touching systems of record",
    weights={"C": 25, "F": 15, "I": 25, "T": 25, "S": 10},
    revisit_triggers=[
        "incumbent's next major-version/licensing change",
        "annual review or governed-door architecture change",
    ],
)

CANDIDATES_W = [
    Candidate(
        name="Incumbent workflow engine",
        family="workflow-first",
        scores={
            "C": Score(4, "returns-coordinator pilot: full TIER-R achievable; AI nodes adequate"),
            "F": Score(4, "self-hosted; infra + platform-team hours modeled; no per-run metering"),
            "I": Score(5, "already wired to gateway, knowledge platform, governed MCP doors"),
            "T": Score(4, "self-hosted data plane; OSS core + reviewed license terms"),
            "S": Score(4, "worker scaling proven at current volume; queue metrics healthy"),
        },
    ),
    Candidate(
        name="Challenger iPaaS suite",
        family="workflow-first",
        scores={
            "C": Score(4, "pilot passed TIER-R; richer connector catalog for ERP edge cases"),
            "F": Score(2, "per-connection licensing at our volume + migration cost of 62 workflows"),
            "I": Score(3, "gateway integration possible; IdP fine; doors need re-wiring"),
            "T": Score(5, "mature certs, strong deprecation policy, enterprise track record"),
            "S": Score(4, "throughput fine at pilot scale; vendor SLAs published"),
        },
    ),
    Candidate(
        name="AI-native no-code platform",
        family="AI-native no-code",
        scores={
            "C": Score(3, "pilot: happy path fast, but idempotency/error-path work fought the tool"),
            "F": Score(2, "credit projection at workhorse volume fails crossover test (tco_model.py)"),
            "I": Score(3, "BYO-key to gateway OK; governed-door wiring partial (webhooks only)"),
            "T": Score(3, "SaaS data plane; terms acceptable with BYO keys; young vendor"),
            "S": Score(3, "burst concurrency limits opaque; vendor gave numbers only on request"),
        },
    ),
]

# ---------------------------------------------------------------------------
# Profile C — the citizen tier: marketing/ops automations built by non-engineers.
# Must be INCAPABLE of touching systems of record except gated read-mostly doors.
# ---------------------------------------------------------------------------
PROFILE_C = TaskProfile(
    name="C (citizen)",
    description="Citizen-builder automations; speed-to-value; bounded blast radius",
    weights={"C": 30, "F": 25, "I": 15, "T": 15, "S": 15},
    revisit_triggers=[
        "re-run at 5x credit volume",
        "vendor funding/acquisition event",
    ],
)

CANDIDATES_C = [
    Candidate(
        name="AI-native no-code platform",
        family="AI-native no-code",
        scores={
            "C": Score(5, "timed session: marketer (not vendor SE) shipped enrichment pipeline in 90 min"),
            "F": Score(4, "credits fail at scale, but BYO-key contract term restores economics"),
            "I": Score(3, "SSO yes; BYO keys via gateway yes; pre-approved connection types configurable"),
            "T": Score(3, "data terms OK with BYO; workspace isolation verified in pilot"),
            "S": Score(4, "latency fine for citizen use; limits acceptable at projected volume"),
        },
    ),
    Candidate(
        name="Incumbent workflow engine",
        family="workflow-first",
        scores={
            "C": Score(2, "timed session: same marketer did not finish; node/expression model too technical"),
            "F": Score(5, "already owned; zero marginal license"),
            "I": Score(5, "fully wired to governed plane"),
            "T": Score(4, "self-hosted"),
            "S": Score(4, "proven"),
        },
    ),
    Candidate(
        name="Suite-bundled automation tool",
        family="workflow-first",
        scores={
            "C": Score(3, "marketers built simple flows; AI steps clumsy in pilot; strong office-suite reach"),
            "F": Score(4, "bundled in existing enterprise agreement; premium connectors extra"),
            "I": Score(3, "IdP native; governed-door wiring awkward outside its own ecosystem"),
            "T": Score(4, "mature vendor terms and certs"),
            "S": Score(3, "throughput fine; per-flow limits documented"),
        },
    ),
]

# ---------------------------------------------------------------------------
# Profile A — the agents: Ch. 11's support agent, Ch. 12's quote-to-order system,
# plus at most two more candidates that pass the team-shaped test.
# ---------------------------------------------------------------------------
PROFILE_A = TaskProfile(
    name="A (agents)",
    description="Deployed agents under full PACT discipline; evaluation-gated",
    weights={"C": 35, "F": 10, "I": 20, "T": 25, "S": 10},
    revisit_triggers=[
        "studio ships tool-level guardrail enforcement (re-test claims)",
        "12 months, whichever comes first",
    ],
)

CANDIDATES_A = [
    Candidate(
        name="Code-first (framework + own code)",
        family="code-first",
        scores={
            "C": Score(5, "Ch. 11 twelve-case eval: 12/12 incl. injection cases; guards fail-safe"),
            "F": Score(3, "engineering time is the cost; ops tooling budgeted"),
            "I": Score(5, "native to gateway, knowledge platform, governed doors, decision log"),
            "T": Score(5, "full control of data plane, guardrails enforced in governed tools"),
            "S": Score(4, "latency engineered to patience budget"),
        },
    ),
    Candidate(
        name="Agent studio",
        family="agent studio",
        scores={
            "C": Score(3, "twelve-case eval vs deployed test agent: 9/12 — failed 3 grounding-refusal cases"),
            "F": Score(4, "fast build; per-agent pricing reasonable at pilot scale"),
            "I": Score(3, "knowledge via our platform API possible; tool guardrails NOT enforceable at tool level yet"),
            "T": Score(3, "'hallucination management' claim tested and documented as partial; PII redaction passed seeded run"),
            "S": Score(4, "conversational latency within budget"),
        },
    ),
    Candidate(
        name="LLM-app platform (self-hosted)",
        family="LLM-app platform",
        scores={
            "C": Score(4, "pilot RAG assistant passed grounding cases; agent features younger than studio's"),
            "F": Score(3, "no license for OSS core; platform-team ops burden real and modeled"),
            "I": Score(4, "self-hosted in VPC; gateway + knowledge platform wiring clean"),
            "T": Score(4, "data plane ours; license terms reviewed; commercial tiers clarified"),
            "S": Score(3, "our cluster, our scaling problem — acceptable"),
        },
    ),
]

# The three selections, in the order the chapter walks them.
MERIDIAN_SELECTIONS = [
    (PROFILE_W, CANDIDATES_W),
    (PROFILE_C, CANDIDATES_C),
    (PROFILE_A, CANDIDATES_A),
]
