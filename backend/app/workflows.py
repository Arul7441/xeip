from __future__ import annotations

from .governance import approval_state, enforce_tenant_scope, require_permission
from .ml import predict_inventory
from .observability import audit_event
from .schemas import InventoryInput, LowTonerWorkflowRequest
from .security import User


def run_low_toner_workflow(payload: LowTonerWorkflowRequest, user: User):
    enforce_tenant_scope(user, payload.governance.tenant_id)
    require_permission(user, "workflow:run")
    toner_level = payload.toner_level_pct
    forecast = predict_inventory(InventoryInput(daily_usage=payload.daily_usage, stock_on_hand=payload.stock_on_hand, horizon_days=payload.horizon_days))
    approval = approval_state(payload.governance, 0.45 if toner_level < 15 else 0.2)
    purchase_order = None
    if (toner_level < 15 or forecast["recommended_action"] == "Trigger procurement") and not approval["human_approval_required"]:
        purchase_order = {
            "po_id": "PO-AUTO-2026-00042",
            "sku": payload.sku,
            "quantity": max(24, int(forecast["forecast_units"] // 10)),
            "status": "submitted_to_procurement",
        }
    audit = audit_event(
        request_id=payload.governance.request_id,
        tenant_id=payload.governance.tenant_id,
        actor=user.subject,
        action="workflow.low_toner",
        resource=payload.sku,
        decision="submitted" if purchase_order else "approval_or_defer",
        controls=["rbac", "tenant_scope", "idempotency_key", "approval_threshold", "audit_log"],
        risk_score=0.45 if toner_level < 15 else 0.2,
        evidence=["inventory_forecast_v1"],
    )
    return {
        "workflow": "low_toner_autonomous_replenishment",
        "initiated_by_role": user.role,
        "steps": [
            "detect low toner",
            "check inventory",
            "forecast future demand",
            "generate purchase order" if purchase_order else "defer purchase order",
            "notify procurement",
            "track completion",
        ],
        "forecast": forecast,
        "purchase_order": purchase_order,
        **approval,
        "audit": audit,
    }
