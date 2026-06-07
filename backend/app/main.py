from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .agents import orchestrate
from .data_quality import dataset_quality_summary
from .governance import enforce_tenant_scope, require_permission
from .ml import predict_churn, predict_failure, predict_inventory
from .rag import answer_with_sources
from .schemas import AgentRequest, ChurnInput, FailureInput, InventoryInput, LowTonerWorkflowRequest, RagQuery
from .security import User, get_current_user, rate_limit, security_headers
from .workflows import run_low_toner_workflow

app = FastAPI(title="XEIP Enterprise Intelligence API", version="1.0.0")


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


@app.get("/health")
def health():
    return {"status": "ok", "service": "xeip-api"}


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
        "data_freshness": "synthetic-demo-2026-06-06",
        "governance_status": "model outputs require approval for high-impact decisions",
    }


@app.post("/agents/orchestrate")
def agent_orchestrate(request: AgentRequest, user: User = Depends(get_current_user)):
    return orchestrate(request, user)


@app.post("/rag/query")
def rag_query(payload: RagQuery, user: User = Depends(get_current_user)):
    enforce_tenant_scope(user, payload.governance.tenant_id)
    return answer_with_sources(payload, user)


@app.post("/ml/failure")
def ml_failure(payload: FailureInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_failure(payload)


@app.post("/ml/churn")
def ml_churn(payload: ChurnInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_churn(payload)


@app.post("/ml/inventory")
def ml_inventory(payload: InventoryInput, user: User = Depends(get_current_user)):
    require_permission(user, "ml:score")
    return predict_inventory(payload)


@app.post("/workflows/low-toner")
def low_toner(payload: LowTonerWorkflowRequest, user: User = Depends(get_current_user)):
    return run_low_toner_workflow(payload, user)


@app.get("/data-quality")
def data_quality(user: User = Depends(get_current_user)):
    require_permission(user, "read:all")
    data_dir = Path(__file__).resolve().parents[2] / "data"
    return dataset_quality_summary(data_dir)
