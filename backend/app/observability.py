from __future__ import annotations

from datetime import datetime
from typing import Any


AUDIT_EVENTS: list[dict[str, Any]] = []


def audit_event(
    *,
    request_id: str,
    tenant_id: str,
    actor: str,
    action: str,
    resource: str,
    decision: str,
    controls: list[str],
    risk_score: float,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    event = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "request_id": request_id,
        "tenant_id": tenant_id,
        "actor": actor,
        "action": action,
        "resource": resource,
        "decision": decision,
        "controls": controls,
        "risk_score": round(risk_score, 3),
        "evidence": evidence or [],
    }
    AUDIT_EVENTS.append(event)
    return event


def system_trace(request_id: str, controls: list[str], warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "controls_applied": controls,
        "warnings": warnings or [],
        "trace_retention": "90d-hot/7y-cold",
    }

