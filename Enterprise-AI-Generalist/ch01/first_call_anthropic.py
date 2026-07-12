"""first_call_anthropic.py — the same request, different provider (book section 1.11.2).

Structural differences from the OpenAI SDK worth noticing:
- system prompt is a top-level parameter, not a message
- input and output tokens are reported separately (and priced differently)
"""
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

response = client.messages.create(
    model="claude-sonnet-5",  # balanced capability/cost; Chapter 2 covers the family
    max_tokens=200,
    system=(
        "You are an enterprise integration analyst. "
        "Answer concisely and flag any assumptions you make."
    ),
    messages=[
        {
            "role": "user",
            "content": (
                "In two sentences, explain what an API gateway does, "
                "for an audience of finance managers."
            ),
        }
    ],
)

print(response.content[0].text)
print(
    f"\nInput tokens: {response.usage.input_tokens}, "
    f"output tokens: {response.usage.output_tokens}"
)
