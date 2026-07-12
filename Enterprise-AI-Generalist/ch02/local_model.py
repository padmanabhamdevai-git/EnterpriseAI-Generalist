"""local_model.py — extend the Chapter 1 wrapper to a local provider (2.11.4).

Requires Ollama (https://ollama.com) with a model pulled:
    ollama pull llama3.2

The point is architectural: because ai_client.py normalized the interface,
adding an entirely different serving pattern — a model running on YOUR
hardware, no data leaving the machine — is ~15 lines.
"""
from ai_client import AIResponse  # Chapter 1's wrapper — see ch02/README.md


def ask_local(prompt: str, system: str = "", model: str = "llama3.2",
              temperature: float = 0.3, max_tokens: int = 500) -> AIResponse:
    """Query a local Ollama model via its OpenAI-compatible API."""
    from openai import OpenAI

    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return AIResponse(
        text=r.choices[0].message.content,
        input_tokens=r.usage.prompt_tokens,
        output_tokens=r.usage.completion_tokens,
        provider=f"local/{model}",
    )


if __name__ == "__main__":
    resp = ask_local(
        "Summarize in two sentences: our Q3 vendor payment run was delayed "
        "four days because invoice matching failed for consolidated POs.",
        system="You are a concise operations analyst.",
    )
    print(f"=== {resp.provider} "
          f"({resp.input_tokens}+{resp.output_tokens} tokens, $0.00) ===")
    print(resp.text)
