"""orchestrator.py — the supervisor pattern from scratch (book 12.11.1).

A supervisor delegates to specialists, collects results, and decides what's
next — holding the plan, the authority, and the SYSTEM-WIDE guards. Built by
hand so the orchestration holds no mystery (as with Ch.11's loop). The
supervisor is an agent whose "tools" are other agents — one level up.

PRODUCTION: graduate to LangGraph (durable state, checkpointing, parallel
delegation). What stays identical: the supervisor holds authority, the SYSTEM
guards, the collective bounding. See ch12/README.md.
"""
import json
from dataclasses import dataclass, field
from typing import Callable

from ai_client import ask


@dataclass
class Specialist:
    name: str
    description: str              # the supervisor chooses specialists by reading this
    run: Callable                 # a Ch.11 agent: (subtask, shared_state) -> result


@dataclass
class SystemGuards:
    """System-LEVEL guards — the multi-agent failure modes live here (§12.7)."""

    max_delegations: int = 15     # total across ALL agents (not per-agent)
    max_tokens: int = 50_000      # TOTAL budget — the #1 multi-agent guard
    tokens_used: int = 0
    delegation_history: list = field(default_factory=list)

    def check(self, delegation: str) -> str | None:
        """Return an escalation reason if any guard trips, else None."""
        if self.tokens_used > self.max_tokens:
            return "total system budget exceeded"
        if len(self.delegation_history) >= self.max_delegations:
            return "delegation limit reached"
        # System loop detection: same delegation pattern repeating.
        if self.delegation_history.count(delegation) >= 2:
            return f"coordination loop: '{delegation}' repeated"
        return None


def _parse(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    try:
        return json.loads(text)
    except Exception:
        return {"action": "escalate", "reasoning": f"unparseable: {raw[:80]}"}


class Supervisor:
    def __init__(self, purpose: str, specialists: list[Specialist],
                 guards: SystemGuards):
        self.purpose = purpose
        self.specialists = {s.name: s for s in specialists}
        self.guards = guards

    def run(self, goal: str) -> dict:
        shared_state = {"goal": goal, "findings": {}}
        trace = []                                    # the UNIFIED trust plane

        while True:
            decision = self._decide(shared_state)
            trace.append({"supervisor": decision})
            action = decision.get("action")

            if action == "finish":
                return {"outcome": "complete", "quote": decision.get("result"),
                        "trace": trace, "state": shared_state}
            if action == "escalate":
                return {"outcome": "escalated", "reason": decision.get("reasoning"),
                        "trace": trace}

            # System guards check BEFORE delegating (the §12.7 containment).
            delegation = f"{action}:{decision.get('subtask', '')[:40]}"
            if reason := self.guards.check(delegation):
                return {"outcome": "escalated", "reason": reason, "trace": trace}
            self.guards.delegation_history.append(delegation)

            specialist = self.specialists.get(action)
            if specialist is None:
                shared_state["findings"]["_error"] = f"no specialist '{action}'"
                trace.append({"_error": f"no specialist '{action}'"})
                continue

            # Delegate. The specialist is a Ch.11 agent — bounded, PACT'd.
            result = specialist.run(decision.get("subtask", ""), shared_state)
            # Validation at the handoff (cascading-failure defense) would go here.
            shared_state["findings"][action] = result
            trace.append({action: result})

    def _decide(self, state: dict) -> dict:
        """The supervisor's own reasoning: what's next, given the goal and
        what specialists have found so far."""
        catalog = "\n".join(f"- {s.name}: {s.description}"
                            for s in self.specialists.values())
        prompt = (
            f"Specialists:\n{catalog}\n\nGoal: {state['goal']}\n"
            f"Findings so far: {json.dumps(state['findings'])}\n\n"
            "Decide the next step. Respond ONLY with JSON: "
            '{"reasoning":"...","action":"specialist_name","subtask":"..."} '
            'or {"action":"finish","result":"..."} '
            'or {"action":"escalate","reasoning":"..."}'
        )
        resp = ask(prompt, system=self.purpose, temperature=0.0, max_tokens=600)
        self.guards.tokens_used += resp.input_tokens + resp.output_tokens
        return _parse(resp.text)
