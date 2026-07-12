"""embeddings_explorer.py — meaning as geometry, made visible (book 5.11.1).

Embeds a handful of enterprise sentences, prints the full similarity
matrix, and demonstrates the property keyword search can never have:
matching by meaning, not by shared words.
"""
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"  # pinned: chunks and queries share it

SENTENCES = [
    "How do I get reimbursed for travel expenses?",          # 0
    "expense claim procedure for business trips",            # 1 — same meaning, ~zero shared words
    "Submit receipts within 30 days of your return.",        # 2 — related policy detail
    "The Sev-1 escalation bridge opens within 15 minutes.",  # 3 — different topic
    "Our cafeteria serves lunch from 11:30 to 14:00.",       # 4 — noise
]


def embed(texts: list[str]) -> np.ndarray:
    """Embed a batch of texts with the pinned model."""
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data])


def cosine_matrix(v: np.ndarray) -> np.ndarray:
    norm = v / np.linalg.norm(v, axis=1, keepdims=True)
    return norm @ norm.T


if __name__ == "__main__":
    vectors = embed(SENTENCES)
    print(f"model={EMBED_MODEL}  dimensions={vectors.shape[1]}\n")

    sim = cosine_matrix(vectors)
    print("similarity matrix (rows/cols = sentence index):")
    header = "      " + "".join(f"  s{j}   " for j in range(len(SENTENCES)))
    print(header)
    for i, row in enumerate(sim):
        print(f"  s{i} " + "".join(f"{x:6.2f} " for x in row))

    print("\nRead it comparatively, not absolutely:")
    print(f"  s0 vs s1 (same meaning, no shared words): {sim[0, 1]:.2f}")
    print(f"  s0 vs s3 (different topics):              {sim[0, 3]:.2f}")
    print(f"  s0 vs s4 (noise):                         {sim[0, 4]:.2f}")
    print("\nThe gap between those numbers IS semantic search.")
