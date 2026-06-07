from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class GovernanceEnvelope(BaseModel):
    request_id: str = Field(..., min_length=8, max_length=80)
    tenant_id: str = Field(..., min_length=3, max_length=80)
    data_classification: Literal["public", "internal", "confidential", "restricted"] = "internal"
    idempotency_key: str | None = Field(default=None, max_length=120)
    business_impact_usd: float = Field(default=0, ge=0)


class AgentRequest(BaseModel):
    objective: str = Field(..., min_length=8, max_length=2000)
    payload: dict = Field(default_factory=dict)
    governance: GovernanceEnvelope

    @field_validator("objective")
    @classmethod
    def objective_must_be_business_request(cls, value: str) -> str:
        if value.strip().lower() in {"help", "test", "do it"}:
            raise ValueError("objective is too vague for autonomous execution")
        return value.strip()


class RagQuery(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000)
    governance: GovernanceEnvelope


class FailureInput(BaseModel):
    temperature: float = Field(..., ge=-20, le=130)
    usage_count: int = Field(..., ge=0, le=2_000_000)
    error_frequency: int = Field(..., ge=0, le=10_000)
    maintenance_history: float = Field(default=0.5, ge=0, le=1)
    toner_level: float = Field(..., ge=0, le=100)


class ChurnInput(BaseModel):
    ticket_count: int = Field(..., ge=0, le=10_000)
    usage_trend: float = Field(..., ge=-1, le=1)
    support_sentiment: float = Field(..., ge=-1, le=1)
    contract_age: int = Field(..., ge=0, le=240)


class TicketRoutingInput(BaseModel):
    summary: str = Field(..., min_length=5, max_length=1000)
    priority: Literal["P1", "P2", "P3", "P4"] = "P3"
    sentiment: float = Field(default=0, ge=-1, le=1)
    device_error_count: int = Field(default=0, ge=0, le=10_000)


class AnomalyInput(BaseModel):
    failed_login_count: int = Field(default=0, ge=0, le=100_000)
    unusual_location: bool = False
    after_hours_access: bool = False
    data_volume_mb: float = Field(default=0, ge=0, le=1_000_000)


class InventoryInput(BaseModel):
    daily_usage: list[float] = Field(..., min_length=3, max_length=365)
    horizon_days: int = Field(default=30, ge=1, le=365)
    stock_on_hand: float = Field(..., ge=0)


class LowTonerWorkflowRequest(BaseModel):
    sku: str = Field(..., min_length=3, max_length=80)
    toner_level_pct: float = Field(..., ge=0, le=100)
    daily_usage: list[float] = Field(..., min_length=3, max_length=365)
    stock_on_hand: float = Field(..., ge=0)
    horizon_days: int = Field(default=30, ge=1, le=365)
    governance: GovernanceEnvelope


class WorkOrderRequest(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=80)
    issue: str = Field(..., min_length=8, max_length=1000)
    priority: Literal["P1", "P2", "P3", "P4"] = "P3"
    governance: GovernanceEnvelope
