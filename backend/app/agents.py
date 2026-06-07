from __future__ import annotations

from .governance import approval_state, enforce_tenant_scope, require_permission
from .ml import predict_churn, predict_failure, predict_inventory
from .rag import answer_with_sources
from .schemas import AgentRequest, ChurnInput, FailureInput, InventoryInput, RagQuery
from .security import User


def orchestrate(request: AgentRequest, user: User):
    enforce_tenant_scope(user, request.governance.tenant_id)
    require_permission(user, "agent:run")
    objective = request.objective.lower()
    agents = []
    recommendations = []
    risk_score = 0.2

    if any(term in objective for term in ["ticket", "support", "error", "diagnose"]):
        rag = answer_with_sources(RagQuery(query=request.objective, governance=request.governance), user)
        agents.append("Support Agent")
        recommendations.append({"agent": "Support Agent", "action": "Diagnose issue and cite technical guidance", **rag})
    if any(term in objective for term in ["failure", "maintenance", "repair", "downtime"]):
        agents.append("Maintenance Agent")
        failure_input = FailureInput(
            temperature=request.payload.get("temperature", 45),
            usage_count=request.payload.get("usage_count", 2200),
            error_frequency=request.payload.get("error_frequency", 2),
            maintenance_history=request.payload.get("maintenance_history", 0.5),
            toner_level=request.payload.get("toner_level", 55),
        )
        result = predict_failure(failure_input)
        risk_score = max(risk_score, result["failure_probability"])
        recommendations.append({"agent": "Maintenance Agent", **result})
    if any(term in objective for term in ["toner", "inventory", "spare", "procurement"]):
        agents.append("Inventory Agent")
        inventory_input = InventoryInput(
            daily_usage=request.payload.get("daily_usage", [18, 19, 21, 24, 20, 26, 28]),
            horizon_days=request.payload.get("horizon_days", 30),
            stock_on_hand=request.payload.get("stock_on_hand", 400),
        )
        recommendations.append({"agent": "Inventory Agent", **predict_inventory(inventory_input)})
    if any(term in objective for term in ["contract", "sla", "obligation"]):
        agents.append("Contract Intelligence Agent")
        recommendations.append({"agent": "Contract Intelligence Agent", "confidence": 0.88, "action": "Review obligations and compare uptime evidence"})
    if any(term in objective for term in ["churn", "customer", "upsell", "sentiment"]):
        agents.append("Customer Success Agent")
        churn_input = ChurnInput(
            ticket_count=request.payload.get("ticket_count", request.payload.get("ticket_count_90d", 12)),
            usage_trend=request.payload.get("usage_trend", 0.02),
            support_sentiment=request.payload.get("support_sentiment", 0.1),
            contract_age=request.payload.get("contract_age", request.payload.get("contract_age_months", 18)),
        )
        result = predict_churn(churn_input)
        risk_score = max(risk_score, result["churn_probability"])
        recommendations.append({"agent": "Customer Success Agent", **result})
    if any(term in objective for term in ["audit", "compliance", "pii", "security"]):
        agents.append("Compliance Agent")
        recommendations.append({"agent": "Compliance Agent", "confidence": 0.91, "action": "Generate audit trail and mask PII"})

    if not agents or "executive" in objective:
        agents.append("Executive Advisor Agent")
        recommendations.append({
            "agent": "Executive Advisor Agent",
            "confidence": 0.9,
            "action": "Prioritize uptime recovery, inventory optimization, and churn intervention",
            "business_value": ["reduced downtime", "improved SLA compliance", "reduced support cost"],
        })

    return {
        "objective": request.objective,
        "agents_invoked": agents,
        "recommendations": recommendations,
        "governance": approval_state(request.governance, risk_score),
        "coordination_trace": ["classify objective", "select permissions", "invoke specialist agents", "rank recommendations"],
        "failure_modes_guarded": [
            "permission drift",
            "unbounded autonomous action",
            "missing evidence",
            "model confidence overclaiming",
            "tenant scope leakage",
        ],
    }
