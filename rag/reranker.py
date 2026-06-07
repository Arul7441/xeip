from __future__ import annotations


def rerank(query: str, retrieved: list[dict]) -> list[dict]:
    terms = set(query.lower().split())
    ranked = []
    for item in retrieved:
        doc = item["document"]
        lexical = sum(1 for term in terms if term in doc.text.lower() or term in doc.domain)
        ranked.append({**item, "rerank_score": round(item["score"] + lexical * 0.15, 4)})
    return sorted(ranked, key=lambda item: item["rerank_score"], reverse=True)

