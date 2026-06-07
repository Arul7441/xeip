from __future__ import annotations

from fastapi import HTTPException

from .schemas import GovernanceEnvelope
from .security import User


APPROVAL_THRESHOLD_USD = 50_000
RESTRICTED_ACTION_ROLES = {"executive", "operations"}


def require_permission(user: User, permission: str) -> None:
    if permission not in user.permissions and "read:all" not in user.permissions:
        raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")


def approval_state(governance: GovernanceEnvelope, action_risk: float) -> dict:
    needs_approval = (
        governance.data_classification == "restricted"
        or governance.business_impact_usd >= APPROVAL_THRESHOLD_USD
        or action_risk >= 0.72
    )
    return {
        "human_approval_required": needs_approval,
        "approval_reason": (
            "restricted data, high business impact, or high model/action risk"
            if needs_approval else "within autonomous execution policy"
        ),
        "policy": "XEIP-AUTONOMY-001",
    }


def enforce_tenant_scope(user: User, tenant_id: str) -> None:
    if user.tenant_id != tenant_id and "read:all" not in user.permissions:
        raise HTTPException(status_code=403, detail="Tenant scope violation")

