# AI Generalist Engineer — Companion Code

Official code repository for the book **AI Generalist Engineer: From AI User to AI Builder** by Padmanabham Venkiteela.

Each chapter's runnable examples live in a `chNN/` folder with its own README. The folders form a deliberate ladder — the same one the book climbs: model calls → prompts as artifacts → grounded knowledge → governed integration → workflows and agents → products → architecture, governance, and operations. Code from later chapters assumes the disciplines (and sometimes the modules) of earlier ones.

## Repository Layout

```
Enterprise-AI-Generalist/
├── ch01/ … ch20/   # one folder per book chapter, each with its own README
├── requirements.txt
├── LICENSE
└── README.md
```

## Prerequisites

- Python 3.10 or later
- An OpenAI API key (https://platform.openai.com) and an Anthropic API key (https://console.anthropic.com) for the chapters that call hosted models — many examples run fully offline

## Setup

```bash
git clone https://github.com/padmanabhamdevai-git/Enterprise-AI-Generalist.git
cd Enterprise-AI-Generalist
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ch01/.env.example ch01/.env   # then edit ch01/.env with your keys
```

Never commit a real `.env` file. The repository `.gitignore` blocks it, but the discipline is yours.

## Chapter Index

| Folder | Chapter | Highlights |
|---|---|---|
| [ch01](ch01/) | The Rise of the Enterprise AI Generalist | First OpenAI/Anthropic calls, provider-agnostic `ai_client`, Cursor rules file |
| [ch02](ch02/) | How Large Language Models Actually Work | Token explorer, temperature lab, evaluation harness, local model via Ollama |
| [ch03](ch03/) | Prompt Engineering: The New Enterprise Interface | Template engine, technique lab (zero/few/CoT), Git-backed prompt registry |
| [ch04](ch04/) | Advanced Prompting and Private AI | Reliability Ladder (Pydantic + repair loops), four-stage pipeline with R4 gates, local/private plane comparison |
| [ch05](ch05/) | Why AI Needs Your Data: RAG Concepts | Embeddings explorer, framework-free RAG in ~100 lines, grounded-vs-ungrounded demo |
| [ch06](ch06/) | Building Production RAG Systems | FastAPI + pgvector service: hybrid search + RRF, re-rank funnel, RAG-triad eval gate, erasure drill |
| [ch07](ch07/) | Enterprise Knowledge Platforms | RLS multi-tenancy, IdP entitlement resolution, connector contract, PII gate at processing |
| [ch08](ch08/) | The Model Context Protocol | MCP client explorer, capability audit (write-tool triage), annotated host configs |
| [ch09](ch09/) | Building and Securing MCP Servers | Mediator + wrapper servers, JWT auth, MCP-aware gateway, cost-center authz, full audit |
| [ch10](ch10/) | Automation Foundations | Idempotency pattern, TIER-R workflow reviewer, importable n8n workflows (deterministic + AI-infused) |
| [ch11](ch11/) | Building Your First AI Agents | ReAct loop from scratch, PACT autonomy map, governed tools, support agent with escalation + injection defense |
| [ch12](ch12/) | Multi-Agent Systems and Orchestration | Supervisor pattern from scratch, system-level guards, concentrated gated authority, governed persistent memory |
| [ch13](ch13/) | The Automation Platform Landscape | C-FIT-S scorecard with sensitivity check, TCO crossover model, Portability Ledger, one workflow built three ways |
| [ch14](ch14/) | Voice Agents and Conversational Interfaces | Turn Budget calculator (three stacks), VOICE brief validator, call evaluator, annotated sample calls |
| [ch15](ch15/) | From Idea to Application | Solution Canvas validator, three worked canvases, Promotion Gates replay, non-goals-first PRD renderer |
| [ch16](ch16/) | Agentic Development with Cursor and Modern IDEs | Mechanical diff pre-reviewer (7-check protocol), clean + trouble sample diffs, org/repo rules templates |
| [ch17](ch17/) | Generative Media for the Enterprise | Asset brief validator, Likeness Register (scope/expiry/revocation), governed media pipeline gates |
| [ch18](ch18/) | The Enterprise AI Architecture Blueprint | Seven-layer blueprint contracts, estate boundary validator, three-rule placement engine |
| [ch19](ch19/) | Security, Governance, and Compliance | Threat Ledger + lethal-trifecta detector, risk-tiering rubric, ARB package completeness gate |
| [ch20](ch20/) | Operating AI at Scale | Unified trace demo (four signal classes), FinOps levers waterfall, maturity-model locator |

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Model identifiers and pricing change frequently; each chapter README notes the models current at the time of writing. Examples are illustrative and require hardening (secret managers, monitoring, error budgets) before production use — the book's later chapters cover exactly that.
