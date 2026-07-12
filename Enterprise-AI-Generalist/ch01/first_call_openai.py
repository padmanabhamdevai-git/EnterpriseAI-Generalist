"""first_call_openai.py — your first programmatic AI request (book section 1.11.1).

Professional habits demonstrated:
- system message establishes role and constraints
- low temperature for repeatable, factual output
- token usage printed on every call (cost awareness from day one)
"""
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads OPENAI_API_KEY from .env

client = OpenAI()  # picks up the key from the environment

response = client.chat.completions.create(
    model="gpt-5.5",  # capable general-purpose model; Chapter 2 covers selection
    messages=[
        {
            "role": "system",
            "content": (
                "You are an enterprise integration analyst. "
                "Answer concisely and flag any assumptions you make."
            ),
        },
        {
            "role": "user",
            "content": (
                "In two sentences, explain what an API gateway does, "
                "for an audience of finance managers."
            ),
        },
    ],
    max_tokens=200,
    temperature=0.3,  # low randomness: suitable for factual, repeatable tasks
)

print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
