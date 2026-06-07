from __future__ import annotations

import hashlib
import math


def embed_text(text: str, dimensions: int = 64) -> list[float]:
    """Deterministic local embedding for offline demos.

    Production can swap this with OpenAI, Azure OpenAI, or an internal embedding model
    without changing the retriever contract.
    """
    vector = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:2], "big") % dimensions
        sign = 1 if digest[2] % 2 == 0 else -1
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))

