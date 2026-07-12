"""ai_client.py — a minimal provider-agnostic wrapper (book section 1.11.3).

Principle 1 in code: the application depends on *our* interface,
not on any vendor's SDK shape. Swapping providers is a one-line change.
"""
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AIResponse:
    """Normalized response, independent of provider."""

    text: str
    input_tokens: int
    output_tokens: int
    provider: str


def ask(
    prompt: str,
    system: str = "",
    provider: str = "anthropic",
    temperature: float = 0.3,
    max_tokens: int = 500,
) -> AIResponse:
    """Send a prompt to the chosen provider and return a normalized response.

    Args:
        prompt: The user request.
        system: Role/behavior instructions for the model.
        provider: "openai" or "anthropic".
        temperature: 0.0 (deterministic) to ~1.0 (creative). Enterprise default: low.
        max_tokens: Hard cap on output length — a cost and latency control.
    """
    if provider == "openai":
        from openai import OpenAI

        r = OpenAI().chat.completions.create(
            model="gpt-5.5",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return AIResponse(
            text=r.choices[0].message.content,
            input_tokens=r.usage.prompt_tokens,
            output_tokens=r.usage.completion_tokens,
            provider="openai",
        )

    if provider == "anthropic":
        import anthropic

        r = anthropic.Anthropic().messages.create(
            model="claude-sonnet-5",
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return AIResponse(
            text=r.content[0].text,
            input_tokens=r.usage.input_tokens,
            output_tokens=r.usage.output_tokens,
            provider="anthropic",
        )

    raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    QUESTION = (
        "List three risks of connecting an AI agent directly "
        "to a production ERP system."
    )
    for p in ("openai", "anthropic"):
        resp = ask(QUESTION, provider=p)
        print(
            f"\n=== {resp.provider} "
            f"({resp.input_tokens}+{resp.output_tokens} tokens) ==="
        )
        print(resp.text)
