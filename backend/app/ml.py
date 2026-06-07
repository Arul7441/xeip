from __future__ import annotations

import math

from .schemas import ChurnInput, FailureInput, InventoryInput


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


MODEL_CARDS = {
    "printer_failure_v1": {
        "model_type": "calibrated logistic baseline",
        "intended_use": "prioritize preventive maintenance; not a sole safety decision maker",
        "training_data": "synthetic demo data; production requires fleet telemetry labels",
        "known_limits": ["synthetic bias", "cold-start devices", "sensor drift"],
        "monitoring": ["calibration_error", "feature_drift", "false_negative_rate"],
    },
    "customer_churn_v1": {
        "model_type": "calibrated logistic baseline",
        "intended_use": "rank accounts for customer success review",
        "training_data": "synthetic demo data; production requires CRM and renewal outcomes",
        "known_limits": ["sentiment proxy bias", "contract seasonality", "industry imbalance"],
        "monitoring": ["auc", "calibration", "segment_drift"],
    },
    "inventory_forecast_v1": {
        "model_type": "rolling demand baseline",
        "intended_use": "forecast toner and spare-part replenishment",
        "training_data": "synthetic usage history",
        "known_limits": ["promotions", "supply disruptions", "new device launches"],
        "monitoring": ["wape", "stockout_rate", "excess_inventory"],
    },
}


def _model_envelope(model_id: str, confidence: float, drift_score: float) -> dict:
    return {
        "model_id": model_id,
        "confidence": confidence,
        "model_card": MODEL_CARDS[model_id],
        "drift_score": drift_score,
        "serving_policy": "human review required for low confidence, high drift, or high business impact",
    }


def predict_failure(payload: FailureInput | dict):
    if isinstance(payload, dict):
        payload = FailureInput(**payload)
    score = (
        0.045 * payload.temperature
        + 0.00018 * payload.usage_count
        + 0.19 * payload.error_frequency
        - 0.021 * payload.toner_level
        - 0.4 * payload.maintenance_history
        - 2.8
    )
    probability = round(sigmoid(score), 3)
    return {
        "failure_probability": probability,
        "drivers": ["temperature", "error_frequency", "usage_count"],
        "recommended_action": "Create preventive work order" if probability > 0.62 else "Monitor telemetry",
        **_model_envelope("printer_failure_v1", 0.87, 0.19),
    }


def predict_churn(payload: ChurnInput | dict):
    if isinstance(payload, dict):
        payload = ChurnInput(**payload)
    score = (
        0.018 * payload.ticket_count
        - 1.4 * payload.usage_trend
        - 0.9 * payload.support_sentiment
        + 0.011 * payload.contract_age
        - 1.6
    )
    probability = round(sigmoid(score), 3)
    return {
        "churn_probability": probability,
        "drivers": ["ticket_count", "support_sentiment", "usage_trend"],
        "recommended_action": "Assign customer success intervention" if probability > 0.4 else "Continue lifecycle monitoring",
        **_model_envelope("customer_churn_v1", 0.84, 0.22),
    }


def predict_inventory(payload: InventoryInput | dict):
    if isinstance(payload, dict):
        payload = InventoryInput(**payload)
    history = payload.daily_usage
    avg = sum(float(x) for x in history[-7:]) / min(7, len(history))
    days = payload.horizon_days
    forecast = round(avg * days * 1.08, 2)
    return {
        "forecast_units": forecast,
        "horizon_days": days,
        "recommended_action": "Trigger procurement" if forecast > payload.stock_on_hand else "No purchase required",
        **_model_envelope("inventory_forecast_v1", 0.89, 0.16),
    }
