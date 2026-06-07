from __future__ import annotations

from .observability import audit_event, system_trace
from .schemas import RagQuery
from .security import User, mask_pii, validate_prompt

KNOWLEDGE = [
    {
        "source": "Maintenance Guide MG-ALTA-2026",
        "text": "High temperature plus repeated 077-900 faults indicates fuser stress. Replace fuser if calibration fails twice.",
        "domain": "maintenance",
        "classification": "internal",
        "required_permission": "read:operations",
    },
    {
        "source": "SOP SUP-114 Ticket Escalation",
        "text": "P1 support cases must be triaged in 15 minutes and escalated when remote recovery fails.",
        "domain": "support",
        "classification": "internal",
        "required_permission": "read:support",
    },
    {
        "source": "Contract Policy SLA-22",
        "text": "Mission critical contracts require 99.5 percent uptime and four hour onsite response.",
        "domain": "contract",
        "classification": "confidential",
        "required_permission": "contract:read",
    },
    {
        "source": "Security Procedure SEC-RAG-9",
        "text": "Retrieved context must be permission filtered, PII masked, and checked for prompt injection instructions.",
        "domain": "security",
        "classification": "restricted",
        "required_permission": "read:audit",
    },
]


def answer_with_sources(request: RagQuery, user: User):
    validation = validate_prompt(request.query)
    controls = ["prompt_injection_scan", "rbac_metadata_filter", "pii_masking", "citation_required"]
    if not validation["allowed"]:
        audit = audit_event(
            request_id=request.governance.request_id,
            tenant_id=request.governance.tenant_id,
            actor=user.subject,
            action="rag.query",
            resource="knowledge_base",
            decision="blocked",
            controls=controls,
            risk_score=1 - validation["score"],
            evidence=["Security Procedure SEC-RAG-9"],
        )
        return {
            "answer": "Request blocked by RAG security validation.",
            "confidence": 0.99,
            "sources": ["Security Procedure SEC-RAG-9"],
            "risk_factors": validation["risk_flags"],
            "audit": audit,
            "trace": system_trace(request.governance.request_id, controls),
        }

    terms = set(request.query.lower().split())
    scored = []
    for doc in KNOWLEDGE:
        if doc["required_permission"] not in user.permissions and "read:all" not in user.permissions:
            continue
        if request.governance.data_classification == "internal" and doc["classification"] == "restricted":
            continue
        score = sum(1 for term in terms if term in doc["text"].lower() or term in doc["domain"])
        if score:
            scored.append((score, doc))
    selected = [doc for _, doc in sorted(scored, key=lambda item: item[0], reverse=True)[:3]]
    if not selected:
        audit = audit_event(
            request_id=request.governance.request_id,
            tenant_id=request.governance.tenant_id,
            actor=user.subject,
            action="rag.query",
            resource="knowledge_base",
            decision="abstained",
            controls=controls,
            risk_score=0.68,
        )
        return {
            "answer": "I do not have enough permission-filtered evidence to answer safely.",
            "confidence": 0.31,
            "sources": [],
            "reasoning": "Retriever found no permitted evidence above threshold.",
            "risk_factors": ["insufficient evidence", "hallucination risk"],
            "alternative_actions": ["open a governed search request", "escalate to domain owner"],
            "audit": audit,
            "trace": system_trace(request.governance.request_id, controls, ["abstained"]),
        }
    context = " ".join(doc["text"] for doc in selected)
    audit = audit_event(
        request_id=request.governance.request_id,
        tenant_id=request.governance.tenant_id,
        actor=user.subject,
        action="rag.query",
        resource="knowledge_base",
        decision="answered",
        controls=controls,
        risk_score=0.18,
        evidence=[doc["source"] for doc in selected],
    )
    return {
        "answer": mask_pii(f"Based on retrieved enterprise guidance: {context}"),
        "confidence": round(min(0.94, 0.62 + len(selected) * 0.11), 2),
        "sources": [doc["source"] for doc in selected],
        "reasoning": "Hybrid retrieval matched operational terms, permission-filtered context, then compressed supporting evidence.",
        "risk_factors": ["limited synthetic KB"] if len(selected) < 2 else [],
        "alternative_actions": ["open service ticket", "schedule preventive maintenance", "request contract review"],
        "role": user.role,
        "audit": audit,
        "trace": system_trace(request.governance.request_id, controls),
    }
