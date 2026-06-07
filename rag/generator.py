from __future__ import annotations


def generate_answer(query: str, ranked_context: list[dict]) -> dict:
    if not ranked_context:
        return {
            "answer": "I do not have enough permission-filtered evidence to answer safely.",
            "confidence": 0.31,
            "sources": [],
        }
    docs = [item["document"] for item in ranked_context[:3]]
    confidence = min(0.94, 0.58 + 0.11 * len(docs) + max(item["rerank_score"] for item in ranked_context[:3]) * 0.08)
    return {
        "answer": " ".join(doc.text for doc in docs),
        "confidence": round(confidence, 2),
        "sources": [doc.source for doc in docs],
        "query": query,
    }

