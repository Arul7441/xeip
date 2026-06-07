from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from . import analytics
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

@app.get("/", response_class=HTMLResponse)
def root():
    return """<!doctype html><html><head><meta charset="utf-8">
<title>XEIP API</title>
<style>body{font-family:system-ui,sans-serif;background:#0a0c10;color:#e6e8eb;
display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}
.card{max-width:560px;padding:40px;text-align:center}
.mark{display:inline-block;background:#e8173a;color:#fff;font-weight:700;
padding:6px 12px;border-radius:8px;font-size:20px}
h1{font-weight:600;margin:18px 0 6px}p{color:#8b929c;line-height:1.6}
a{display:inline-block;margin:8px;padding:10px 18px;border-radius:8px;
background:#1a1d24;color:#e6e8eb;text-decoration:none;border:1px solid #2a2e37}
a:hover{border-color:#e8173a}.ok{color:#22c55e}</style></head>
<body><div class="card">
<span class="mark">XEIP</span>
<h1>Enterprise Intelligence API <span class="ok">&#9679; live</span></h1>
<p>This is the backend API. It serves data to the XEIP dashboard.<br>
Pick a destination below.</p>
<div>
<a href="https://arul7441.github.io/xeip/">Open Dashboard</a>
<a href="/docs">API Explorer (/docs)</a>
<a href="/health">Health Check</a>
</div>
<p style="margin-top:24px;font-size:12px">v2.0.0 &middot; FastAPI &middot; governed by XEIP-AUTONOMY-001</p>
</div></body></html>"""


@app.get("/health")
def health():
    return {"status": "ok", "service": "xeip-api", "version": "2.0.0"}


@app.get("/metrics/executive")
def executive_metrics(user: User = Depends(get_current_user)):
    return analytics.executive_metrics(role=user.role, tenant_id=user.tenant_id)


@app.get("/metrics/roi")
def roi_metrics(user: User = Depends(get_current_user)):
    """Transparent ROI — annual savings by lever with stated assumptions."""
    return analytics.roi_summary()


@app.get("/sustainability")
def sustainability(user: User = Depends(get_current_user)):
    """ESG view — energy, carbon, duplex/color mix, waste from failed jobs."""
    return analytics.sustainability()


@app.get("/document-intelligence")
def document_intelligence(user: User = Depends(get_current_user)):
    """Intelligent Document Processing — OCR confidence, exceptions, fraud, STP rate."""
    return analytics.document_intelligence()


@app.get("/responsible-ai")
def responsible_ai(user: User = Depends(get_current_user)):
    """Responsible-AI posture — NIST AI RMF + EU AI Act mapping, model cards, compliance, security."""
    return analytics.responsible_ai()


@app.get("/executive-brief")
def executive_brief(user: User = Depends(get_current_user)):
    """One-page executive brief generated from live data."""
    return analytics.executive_brief()


class AgenticRequest(BaseModel):
    device_id: Optional[str] = Field(default=None, max_length=40)
    governance: GovernanceEnvelope


@app.post("/agentic/run")
def agentic_run(payload: AgenticRequest, user: User = Depends(get_current_user)):
    """Hero agentic workflow — Sensor -> Inventory -> Forecast -> Procurement (governed) -> Maintenance."""
    enforce_tenant_scope(user, payload.governance.tenant_id)
    return analytics.agentic_workflow(device_id=payload.device_id,
                                      request_id=payload.governance.request_id)


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
    return copilot_query(payload.query)
