from __future__ import annotations

import math
import random
from typing import Optional


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


DEVICE_MODELS = ["Xerox VersaLink C405", "Xerox AltaLink C8155", "Xerox WorkCentre 6515",
                 "Xerox PrimeLink C9065", "Xerox VersaLink B405"]

LOCATIONS = ["Floor 1 - East Wing", "Floor 2 - West Wing", "Floor 3 - Conference",
             "Floor 4 - Executive", "Basement - Print Room"]

STATUS_OPTIONS = ["online", "online", "online", "online", "warning", "offline"]


def _make_device(seed: int) -> dict:
    rng = random.Random(seed)
    model = rng.choice(DEVICE_MODELS)
    location = rng.choice(LOCATIONS)
    status = rng.choice(STATUS_OPTIONS)
    toner = round(rng.uniform(5, 100), 1)
    temp = round(rng.uniform(18, 85), 1)
    usage = rng.randint(1000, 500000)
    errors = rng.randint(0, 40)
    maintenance = round(rng.uniform(0.2, 1.0), 2)

    # Compute failure probability using same sigmoid logic as ml.py
    score = (
        0.045 * temp
        + 0.00018 * usage
        + 0.19 * errors
        - 0.021 * toner
        - 0.4 * maintenance
        - 2.8
    )
    failure_prob = round(_sigmoid(score), 3)

    if failure_prob > 0.62:
        alert = "high"
    elif failure_prob > 0.35:
        alert = "medium"
    else:
        alert = "low"

    return {
        "device_id": f"XRX-{seed:04d}",
        "model": model,
        "location": location,
        "status": status,
        "toner_level_pct": toner,
        "temperature_c": temp,
        "usage_count": usage,
        "error_count_30d": errors,
        "failure_probability": failure_prob,
        "alert_level": alert,
        "recommended_action": (
            "Schedule immediate maintenance" if alert == "high"
            else "Monitor closely" if alert == "medium"
            else "No action required"
        ),
        "last_seen": "2026-06-08T10:00:00Z",
    }


def get_fleet_live(limit: int = 10, alert_filter: Optional[str] = None) -> dict:
    limit = max(1, min(limit, 50))
    devices = [_make_device(i) for i in range(1, 51)]

    if alert_filter:
        devices = [d for d in devices if d["alert_level"] == alert_filter]

    devices = devices[:limit]

    total = len(devices)
    high = sum(1 for d in devices if d["alert_level"] == "high")
    medium = sum(1 for d in devices if d["alert_level"] == "medium")
    low = sum(1 for d in devices if d["alert_level"] == "low")
    avg_toner = round(sum(d["toner_level_pct"] for d in devices) / total, 1) if total else 0

    return {
        "fleet_summary": {
            "total_devices_shown": total,
            "high_alert": high,
            "medium_alert": medium,
            "low_alert": low,
            "avg_toner_pct": avg_toner,
        },
        "devices": devices,
        "data_freshness": "live-synthetic-2026-06-08",
    }


def get_fleet_stats() -> dict:
    devices = [_make_device(i) for i in range(1, 51)]
    total = len(devices)
    online = sum(1 for d in devices if d["status"] == "online")
    warning = sum(1 for d in devices if d["status"] == "warning")
    offline = sum(1 for d in devices if d["status"] == "offline")
    high_risk = sum(1 for d in devices if d["alert_level"] == "high")
    avg_toner = round(sum(d["toner_level_pct"] for d in devices) / total, 1)
    avg_failure = round(sum(d["failure_probability"] for d in devices) / total, 3)

    return {
        "total_fleet": total,
        "online": online,
        "warning": warning,
        "offline": offline,
        "high_risk_devices": high_risk,
        "avg_toner_pct": avg_toner,
        "avg_failure_probability": avg_failure,
        "fleet_health_score": round((online / total) * 100 * (1 - avg_failure), 1),
    }
