from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .agents import orchestrate
from .copilot import copilot_query
from .data_quality import dataset_quality_summary
from .fleet import get_fleet_live, get_fleet_stats
from .governance import enforce_tenant_scope, require_permission
from .ml import detect_anomaly, predict_churn, predict_failure, predict_inventory, route_ticket
from .rag import answer_with_sources
from .schemas import (
    AgentRequest,
    AnomalyInput,
    ChurnInput,
    FailureInput,
    GovernanceEnvelope,
    InventoryInput,
    LowTonerWorkflowRequest,
    RagQuery,
    TicketRoutingInput,
    WorkOrderRequest,
)
from .security import User, get_current_user, rate_limit, security_headers
from .workflows import run_low_toner_workflow

app = FastAPI(title="XEIP Enterprise Intelligence API", version="2.0.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def enterprise_controls(request: Request, call_next):
    rate_limit(request)
    response = await call_next(request)
    for key, value in security_headers().items():
        response.headers[key] = value
    return response


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


# ── Core ──────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "xeip-api", "version": "2.0.0"}


@app.get("/metrics/executive")
def executive_metrics(user: User = Depends(get_current_user)):
    return {
        "mttr_hours": 14.8,
        "device_uptime_pct": 98.73,
        "cost_savings_usd": 4_820_000,
        "ticket_resolution_hours": 12.6,
        "churn_risk_pct": 11.4,
        "sla_compliance_pct": 96.8,
        "inventory_health_pct": 91.2,
        "ai_agent_productivity_pct": 68.5,
        "forecast_accuracy_pct": 89.7,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "data_freshness": "synthetic-demo-2026-06-08",
        "governance_status": "model outputs require approval for high-impact decisions",
    }


# ── Agents ────────────────────────────────────────────────────────────────────

@app.post("/agents/orchestrate")
def agent_orchestrate(request: AgentRequest, user: User = Depends(get_current_user)):
    return orchestrate(request, user)


@app.post("/chat")
def chat(request: AgentRequest, user: User = Depends(get_current_user)):
    return orchestrate(request, user)


# ── RAG ───────────────────────────────────────────────────────────────────────

@app.post("/rag/query")
def rag_query(payload: RagQuery, user: User = Depends(get_current_user)):
    enforce_tenant_scope(user, payload.governance.tenant_id)
    return answer_with_sources(payload, user)


# ── ML ────────────────────────────────────────────────────────────────────────

@app.post("/ml/failure")
def ml_failure(payload: FailureInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_failure(payload)


@app.post("/predict-failure")
def predict_failure_alias(payload: FailureInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_failure(payload)


@app.post("/ml/churn")
def ml_churn(payload: ChurnInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_churn(payload)


@app.post("/predict-churn")
def predict_churn_alias(payload: ChurnInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_churn(payload)


@app.post("/ml/inventory")
def ml_inventory(payload: InventoryInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_inventory(payload)


@app.post("/forecast-toner")
def forecast_toner(payload: InventoryInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_inventory(payload)


@app.post("/route-ticket")
def route_ticket_endpoint(payload: TicketRoutingInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return route_ticket(payload)


@app.post("/detect-anomaly")
def detect_anomaly_endpoint(payload: AnomalyInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return detect_anomaly(payload)


# ── Workflows ─────────────────────────────────────────────────────────────────

@app.post("/workflows/low-toner")
def low_toner(payload: LowTonerWorkflowRequest, user: User = Depends(get_current_user)):
    return run_low_toner_workflow(payload, user)


@app.post("/create-workorder")
def create_workorder(payload: WorkOrderRequest, user: User = Depends(get_current_user)):
    enforce_tenant_scope(user, payload.governance.tenant_id)
    require_permission(user, "workflow:run")
    return {
        "workorder_id": f"WO-{payload.device_id.upper()}-2026-0001",
        "device_id": payload.device_id,
        "priority": payload.priority,
        "status": "created",
        "assignment": "field_maintenance" if payload.priority in {"P1", "P2"} else "standard_support",
        "governance": {
            "request_id": payload.governance.request_id,
            "tenant_id": payload.governance.tenant_id,
            "policy": "XEIP-WORKFLOW-001",
        },
    }


@app.post("/analyze-contract")
def analyze_contract(payload: RagQuery, user: User = Depends(get_current_user)):
    enforce_tenant_scope(user, payload.governance.tenant_id)
    require_permission(user, "contract:read")
    result = answer_with_sources(payload, user)
    return {
        "contract_analysis": result["answer"],
        "sla_risk": "high" if "99.5" in result["answer"] else "needs_review",
        "sources": result["sources"],
        "confidence": result["confidence"],
        "audit": result["audit"],
    }


@app.get("/data-quality")
def data_quality(user: User = Depends(get_current_user)):
    require_permission(user, "read:all")
    data_dir = Path(__file__).resolve().parents[2] / "data"
    return dataset_quality_summary(data_dir)


# ── Fleet Intelligence (NEW) ──────────────────────────────────────────────────

@app.get("/fleet/live")
def fleet_live(
    limit: int = Query(default=10, ge=1, le=50),
    alert: Optional[str] = Query(default=None, description="Filter by alert level: high, medium, low"),
    user: User = Depends(get_current_user),
):
    """Live fleet telemetry — device status, toner levels, failure risk for all printers."""
    require_permission(user, "ml:score")
    return get_fleet_live(limit=limit, alert_filter=alert)


@app.get("/fleet/stats")
def fleet_stats(user: User = Depends(get_current_user)):
    """Aggregated fleet health statistics."""
    require_permission(user, "ml:score")
    return get_fleet_stats()


# ── Executive Copilot (NEW) ───────────────────────────────────────────────────

class CopilotRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    governance: GovernanceEnvelope


@app.post("/copilot/query")
def copilot(payload: CopilotRequest, user: User = Depends(get_current_user)):
    """Executive AI Copilot — natural language queries about fleet, SLA, churn, costs."""
    enforce_tenant_scope(user, payload.governance.tenant_id)
    return copilot_query(payload.query, role=user.role)
