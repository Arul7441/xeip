from __future__ import annotations

from dataclasses import dataclass

from .embeddings import cosine_similarity, embed_text


@dataclass(frozen=True)
class RagDocument:
    source: str
    text: str
    domain: str
    classification: str
    required_permission: str


DOCUMENTS = [
    RagDocument("manuals/MG-ALTA-2026.md", "High temperature plus repeated 077-900 faults indicates fuser stress.", "maintenance", "internal", "read:operations"),
    RagDocument("sop/SUP-114.md", "P1 support cases must be triaged in 15 minutes and escalated when remote recovery fails.", "support", "internal", "read:support"),
    RagDocument("contracts/SLA-22.md", "Mission critical contracts require 99.5 percent uptime and four hour onsite response.", "contract", "confidential", "contract:read"),
    RagDocument("tickets/TICKET-RAG-SEC.md", "Retrieved context must be permission filtered, PII masked, and checked for prompt injection.", "security", "restricted", "read:audit"),
]


def retrieve(query: str, permissions: set[str], top_k: int = 4) -> list[dict]:
    query_vector = embed_text(query)
    rows = []
    for doc in DOCUMENTS:
        if doc.required_permission not in permissions and "read:all" not in permissions:
            continue
        score = cosine_similarity(query_vector, embed_text(f"{doc.domain} {doc.text}"))
        rows.append({"score": round(score, 4), "document": doc})
    return sorted(rows, key=lambda item: item["score"], reverse=True)[:top_k]

