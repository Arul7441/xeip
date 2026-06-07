from __future__ import annotations

import csv
import math
import pathlib
from typing import Optional

DATA = pathlib.Path(__file__).parent.parent.parent / "data"


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _f(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _load_telemetry():
    p = DATA / "printer_telemetry.csv"
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _build_devices():
    """Aggregate raw telemetry into one record per physical device.

    Uses the latest reading per device for live fields, and the same sigmoid
    failure model as ml.py. Output schema matches the original synthetic fleet
    so the dashboard Fleet Monitor works unchanged.
    """
    rows = _load_telemetry()
    by_device: dict[str, list[dict]] = {}
    for r in rows:
        did = r.get("device_id", "")
        if did:
            by_device.setdefault(did, []).append(r)

    devices = []
    for did, readings in by_device.items():
        readings.sort(key=lambda r: r.get("timestamp", ""))
        latest = readings[-1]

        # Latest non-blank value wins; fall back to sensible defaults.
        def latest_val(col, default):
            for r in reversed(readings):
                if r.get(col) not in ("", None):
                    return _f(r[col], default)
            return default

        toner = round(latest_val("toner_level_pct", 50.0), 1)
        temp = round(latest_val("temperature_c", 40.0), 1)
        usage = int(latest_val("usage_count", 0))
        errors = int(latest_val("error_frequency", 0))
        anomaly = any(r.get("anomaly_flag") == "True" for r in readings)
        model = latest.get("model", "Unknown")
        region = latest.get("region", "Unknown")
        customer = latest.get("customer", "Unknown")
        last_seen = latest.get("timestamp", "")

        # Failure probability — same coefficients as ml.py / original fleet model.
        score = (0.045 * temp + 0.00018 * usage + 0.19 * errors
                 - 0.021 * toner - 0.4 * 0.5 - 2.8)
        failure_prob = round(_sigmoid(score), 3)

        # Status derived from real signals (no explicit status column exists).
        if anomaly or temp > 78:
            status = "offline"
        elif toner < 15 or temp > 55 or errors > 12:
            status = "warning"
        else:
            status = "online"

        if failure_prob > 0.62:
            alert = "high"
        elif failure_prob > 0.35:
            alert = "medium"
        else:
            alert = "low"

        devices.append({
            "device_id": did,
            "model": model,
            "location": f"{region} · {customer}",
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
            "last_seen": last_seen,
        })

    # Worst devices first so the monitor surfaces problems immediately.
    devices.sort(key=lambda d: d["failure_probability"], reverse=True)
    return devices


# Cached once — telemetry is static.
DEVICES = _build_devices()


def get_fleet_live(limit: int = 10, alert_filter: Optional[str] = None) -> dict:
    limit = max(1, min(limit, 50))
    pool = [d for d in DEVICES if not alert_filter or d["alert_level"] == alert_filter]
    shown = pool[:limit]

    total = len(shown)
    high = sum(1 for d in shown if d["alert_level"] == "high")
    medium = sum(1 for d in shown if d["alert_level"] == "medium")
    low = sum(1 for d in shown if d["alert_level"] == "low")
    avg_toner = round(sum(d["toner_level_pct"] for d in shown) / total, 1) if total else 0

    return {
        "fleet_summary": {
            "total_devices_shown": total,
            "matched_devices": len(pool),
            "high_alert": high,
            "medium_alert": medium,
            "low_alert": low,
            "avg_toner_pct": avg_toner,
        },
        "devices": shown,
        "data_freshness": "live-telemetry · printer_telemetry.csv",
    }


def get_fleet_stats() -> dict:
    devices = DEVICES
    total = len(devices)
    if not total:
        return {"total_fleet": 0}
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
