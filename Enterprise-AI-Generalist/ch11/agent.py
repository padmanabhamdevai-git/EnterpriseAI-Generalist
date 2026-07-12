"""agent.py — the ReAct loop from scratch (book 11.11.1).

An agent is a model in a while loop deciding: am I done, or do I need a tool?
This is the whole mystery. Frameworks elaborate on this; they don't replace it.
~120 lines, and you'll never be confused by an agent framework again.

NOTE: this uses a JSON-in-text decision protocol so it runs against the Ch.1
ask() wrapper without native tool-calling — pedagogical, for legibility.
Production agents use the SDK's native tool-calling (structured, more robust).
"""
import json
from dataclasses import dataclass
from typing import Callable

from ai_client import ask   # Chapter 1's wrapper


@dataclass
class Tool:
    name: str
    description: str          # the model chooses tools by reading this (Ch.8)
    run: Callable[[dict], str]
    autonomy: str = "full"    # "full" or "approval" (the A in PACT)


class Agent:
    def __init__(self, goal_system: str, tools: list[Tool], max_steps: int = 12):
        self.system = goal_system
        self.tools = {t.name: t for t in tools}
        self.max_steps = max_steps        # the guard that prevents infinite loops

    def _tool_catalog(self) -> str:
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())

    def run(self, task: str, approve=lambda t, a: True) -> dict:
        """The ReAct loop. `approve` gates 'approval'-autonomy tools (Copilot)."""
        context = [f"TASK: {task}"]
        trace = []                         # the decision log — the trust plane
        seen_actions = set()               # loop detection

        for step in range(self.max_steps):
            # REASON: the model decides the next action or finishes.
            prompt = (
                f"Tools available:\n{self._tool_catalog()}\n\n"
                "History so far:\n" + "\n".join(context) + "\n\n"
                "Decide the next step. Respond ONLY with JSON:\n"
                '{"reasoning": "...", "action": "tool_name", "args": {...}}\n'
                "or, if the goal is met or you cannot proceed:\n"
                '{"reasoning": "...", "action": "finish", "result": "..."}\n'
                'Use action "escalate" to hand off to a human.'
            )
            raw = ask(prompt, system=self.system, temperature=0.0,
                      max_tokens=500).text
            decision = _parse(raw)
            trace.append({"step": step, **decision})
            action = decision.get("action")

            # FINISH / ESCALATE — terminal outcomes.
            if action == "finish":
                return {"outcome": "resolved", "result": decision.get("result"),
                        "steps": step + 1, "trace": trace}
            if action == "escalate":
                return {"outcome": "escalated", "reason": decision.get("reasoning"),
                        "steps": step + 1, "trace": trace}

            tool = self.tools.get(action)
            if tool is None:
                context.append(f"OBSERVE: no such tool '{action}'. Reconsider.")
                continue

            # Loop detection: same tool + args twice → stuck → escalate.
            sig = f"{action}:{json.dumps(decision.get('args', {}), sort_keys=True)}"
            if sig in seen_actions:
                return {"outcome": "escalated", "reason": "loop detected",
                        "steps": step + 1, "trace": trace}
            seen_actions.add(sig)

            # AUTONOMY gate (the A in PACT): approval-tools need a human yes.
            if tool.autonomy == "approval" and not approve(action, decision.get("args", {})):
                context.append(f"OBSERVE: human declined {action}. Reconsider.")
                continue

            # ACT + OBSERVE
            result = tool.run(decision.get("args", {}))
            context.append(f"ACT: {action}({decision.get('args', {})})")
            context.append(f"OBSERVE: {result}")

        # Step limit hit without finishing → escalate, never silently give up.
        return {"outcome": "escalated", "reason": "step limit reached",
                "steps": self.max_steps, "trace": trace}


def _parse(raw: str) -> dict:
    """Fail SAFE: unparseable output escalates (the Ch.7 PII-gate posture)."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    try:
        return json.loads(text)
    except Exception:
        return {"action": "escalate",
                "reasoning": f"unparseable decision: {raw[:100]}"}


# --- A minimal research agent so `python agent.py` shows the loop reasoning ---
if __name__ == "__main__":
    def _calc(args):
        try:
            return str(eval(args.get("expression", ""), {"__builtins__": {}}))
        except Exception as e:
            return f"error: {e}"

    def _note(args):
        return f"noted: {args.get('text', '')}"

    demo_tools = [
        Tool("calculator", "Evaluate a math expression. args: expression.", _calc),
        Tool("scratchpad", "Record an intermediate finding. args: text.", _note),
    ]
    a = Agent(
        "You are a research assistant. Use tools to work through the task "
        "step by step, then finish with the answer.",
        demo_tools, max_steps=8,
    )
    out = a.run("A return costs $180. Restocking is 15%. If waived, how much "
                "does the customer get back? Compute it, note the result, finish.")
    print(f"\noutcome: {out['outcome']} ({out['steps']} steps)")
    for e in out["trace"]:
        print(f"  step {e['step']}: {e.get('action')} — {e.get('reasoning','')[:70]}")
    if out["outcome"] == "resolved":
        print(f"  RESULT: {out['result']}")
