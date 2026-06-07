from __future__ import annotations

import csv
import json
import math
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

CUSTOMERS = [
    "Aster Financial", "Northwind Health", "Vertex Legal", "Summit Manufacturing",
    "BluePeak Retail", "CivicGrid Utilities", "Meridian Insurance", "Atlas Education",
    "Pioneer Logistics", "Helio Energy", "Cobalt Media", "Arbor Pharma",
]
MODELS = ["Xerox AltaLink C8155", "Xerox VersaLink B625", "Xerox PrimeLink C9070", "Xerox B315", "Xerox C410"]
REGIONS = ["US-East", "US-West", "EU-Central", "APAC-South", "LATAM"]
DEPARTMENTS = ["Finance", "Legal", "HR", "Operations", "Engineering", "Procurement", "Support"]
START = datetime(2024, 1, 1)
END = datetime(2026, 6, 1)


def rand_time() -> str:
    delta = END - START
    return (START + timedelta(seconds=random.randint(0, int(delta.total_seconds())))).isoformat(timespec="seconds")


def maybe(value, p=0.03):
    return "" if random.random() < p else value


def write_csv(name: str, fields: list[str], rows: list[dict]):
    path = DATA_DIR / f"{name}.csv"
    if rows:
        rows.append(dict(rows[random.randrange(len(rows))]))
        rows[-1]["duplicate_marker"] = "duplicate"
    fields = fields + (["duplicate_marker"] if "duplicate_marker" not in fields else [])
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def device_id(i: int) -> str:
    return f"XRX-{100000 + i % 2200}"


def gen_printer_telemetry(n=5000):
    rows = []
    for i in range(n):
        usage = max(0, int(random.gauss(2100, 850)))
        anomaly = random.random() < 0.025
        rows.append({
            "event_id": str(uuid.uuid4()),
            "timestamp": rand_time(),
            "device_id": device_id(i),
            "customer": random.choice(CUSTOMERS),
            "region": random.choice(REGIONS),
            "model": random.choice(MODELS),
            "temperature_c": maybe(round(random.gauss(46, 8) + (35 if anomaly else 0), 2)),
            "humidity_pct": maybe(round(random.uniform(25, 76), 2)),
            "usage_count": usage * (6 if anomaly else 1),
            "paper_jam_rate": round(max(0, random.gauss(0.018, 0.014)), 4),
            "toner_level_pct": maybe(max(0, min(100, int(random.gauss(54, 28))))),
            "error_frequency": max(0, int(random.gauss(2, 2) + (18 if anomaly else 0))),
            "anomaly_flag": anomaly,
        })
    return rows


def gen_toner_usage(n=5000):
    return [{
        "usage_id": str(uuid.uuid4()), "timestamp": rand_time(), "device_id": device_id(i),
        "customer": random.choice(CUSTOMERS), "cartridge_type": random.choice(["black", "cyan", "magenta", "yellow"]),
        "pages_printed": max(0, int(random.gauss(1400, 650))),
        "toner_consumed_ml": maybe(round(max(0.1, random.gauss(38, 15)), 2)),
        "remaining_pct": max(0, min(100, int(random.gauss(48, 31)))),
        "replacement_required": random.random() < 0.13,
    } for i in range(n)]


def gen_maintenance_logs(n=5000):
    return [{
        "maintenance_id": str(uuid.uuid4()), "timestamp": rand_time(), "device_id": device_id(i),
        "technician_id": f"TECH-{random.randint(100, 260)}", "maintenance_type": random.choice(["preventive", "corrective", "firmware", "calibration"]),
        "parts_replaced": random.choice(["none", "fuser", "roller kit", "transfer belt", "toner sensor", "ADF motor"]),
        "downtime_minutes": max(0, int(random.gauss(72, 42))),
        "cost_usd": round(max(0, random.gauss(310, 180)), 2),
        "maintenance_history_score": round(random.uniform(0.2, 0.98), 3),
        "notes": random.choice(["resolved", "follow up required", "device aging", "customer unavailable", "remote fix applied"]),
    } for i in range(n)]


def gen_error_logs(n=5000):
    codes = ["010-331", "077-900", "024-747", "116-324", "091-312", "042-326"]
    return [{
        "error_id": str(uuid.uuid4()), "timestamp": rand_time(), "device_id": device_id(i),
        "error_code": random.choice(codes), "severity": random.choice(["low", "medium", "high", "critical"]),
        "subsystem": random.choice(["print_engine", "network", "scanner", "finisher", "security", "supply"]),
        "auto_recovered": random.random() < 0.54,
        "error_duration_sec": max(1, int(random.expovariate(1 / 180))),
    } for i in range(n)]


def gen_service_tickets(n=5000):
    cats = ["hardware", "software", "network", "configuration", "maintenance"]
    return [{
        "ticket_id": str(uuid.uuid4()), "opened_at": rand_time(), "customer": random.choice(CUSTOMERS),
        "device_id": device_id(i), "category": random.choice(cats), "priority": random.choice(["P1", "P2", "P3", "P4"]),
        "sentiment": round(random.uniform(-0.95, 0.85), 3), "resolution_hours": round(max(0.2, random.gauss(18, 12)), 2),
        "sla_met": random.random() < 0.86, "escalated": random.random() < 0.16,
        "summary": random.choice(["paper jam repeats", "driver install failed", "scan to email broken", "poor print quality", "device offline"]),
    } for i in range(n)]


def gen_support_conversations(n=5000):
    return [{
        "conversation_id": str(uuid.uuid4()), "timestamp": rand_time(), "customer": random.choice(CUSTOMERS),
        "channel": random.choice(["chat", "email", "phone", "portal"]), "intent": random.choice(["troubleshoot", "billing", "setup", "escalation", "how_to"]),
        "turn_count": random.randint(2, 24), "sentiment": round(random.uniform(-1, 1), 3),
        "contains_pii": random.random() < 0.07, "resolved": random.random() < 0.79,
        "transcript_excerpt": random.choice(["device shows fault code", "need invoice copy", "cannot authenticate", "toner depleted", "contract question"]),
    } for _ in range(n)]


def gen_contracts(n=5000):
    return [{
        "contract_id": str(uuid.uuid4()), "customer": random.choice(CUSTOMERS), "effective_date": rand_time()[:10],
        "term_months": random.choice([12, 24, 36, 48, 60]), "sla_uptime_pct": random.choice([97.5, 98.0, 99.0, 99.5]),
        "response_time_hours": random.choice([2, 4, 8, 24]), "monthly_value_usd": round(random.uniform(3000, 125000), 2),
        "renewal_risk": round(random.random(), 3), "obligation_count": random.randint(8, 44),
        "violation_count": random.choices([0, 1, 2, 3, 5], weights=[70, 14, 8, 5, 3])[0],
    } for _ in range(n)]


def gen_invoice_processing(n=5000):
    return [{
        "invoice_id": str(uuid.uuid4()), "timestamp": rand_time(), "customer": random.choice(CUSTOMERS),
        "amount_usd": round(max(25, random.gauss(8400, 6400)), 2), "currency": random.choice(["USD", "EUR", "GBP", "INR"]),
        "ocr_confidence": round(random.uniform(0.72, 0.999), 3), "exception_type": random.choice(["none", "missing_po", "tax_mismatch", "duplicate", "vendor_mismatch"]),
        "approval_cycle_hours": round(max(1, random.gauss(46, 31)), 2),
        "fraud_score": round(random.betavariate(1.2, 9), 3),
    } for _ in range(n)]


def gen_workflow_logs(n=5000):
    return [{
        "workflow_id": str(uuid.uuid4()), "timestamp": rand_time(), "employee_id": f"EMP-{random.randint(1000, 9900)}",
        "department": random.choice(DEPARTMENTS), "process": random.choice(["invoice", "contract_review", "device_onboarding", "ticket_triage", "procurement"]),
        "duration_minutes": round(max(1, random.gauss(95, 70)), 2), "automation_candidate": random.random() < 0.42,
        "rework_count": random.randint(0, 5), "policy_exception": random.random() < 0.06,
    } for _ in range(n)]


def gen_print_jobs(n=5000):
    return [{
        "job_id": str(uuid.uuid4()), "timestamp": rand_time(), "device_id": device_id(i), "customer": random.choice(CUSTOMERS),
        "user_department": random.choice(DEPARTMENTS), "pages": max(1, int(random.expovariate(1 / 28))),
        "color": random.random() < 0.38, "duplex": random.random() < 0.64, "job_status": random.choice(["completed", "cancelled", "failed", "held"]),
        "sensitive_doc_detected": random.random() < 0.09,
    } for i in range(n)]


def gen_customer_profiles(n=5000):
    return [{
        "customer_id": str(uuid.uuid4()), "customer": random.choice(CUSTOMERS), "industry": random.choice(["finance", "healthcare", "legal", "manufacturing", "retail", "public_sector"]),
        "region": random.choice(REGIONS), "fleet_size": random.randint(12, 1800), "annual_contract_value": round(random.uniform(25000, 5500000), 2),
        "ticket_count_90d": random.randint(0, 140), "usage_trend": round(random.uniform(-0.45, 0.62), 3),
        "support_sentiment": round(random.uniform(-0.85, 0.9), 3), "contract_age_months": random.randint(1, 72),
        "churn_probability": round(random.betavariate(1.6, 6), 3),
    } for _ in range(n)]


def gen_product_catalog(n=5000):
    return [{
        "sku": f"XRX-SKU-{i:05d}", "product_name": random.choice(MODELS + ["Toner 006R04399", "Fuser 115R00138", "Transfer Belt 001R00613"]),
        "category": random.choice(["device", "toner", "spare_part", "software", "service"]),
        "unit_cost_usd": round(random.uniform(18, 18800), 2), "lead_time_days": random.randint(1, 60),
        "supplier_risk": round(random.random(), 3), "stock_on_hand": random.randint(0, 900),
        "reorder_point": random.randint(10, 260), "active": random.random() < 0.94,
    } for i in range(n)]


def gen_warranty_records(n=5000):
    return [{
        "warranty_id": str(uuid.uuid4()), "device_id": device_id(i), "customer": random.choice(CUSTOMERS),
        "start_date": rand_time()[:10], "duration_months": random.choice([12, 24, 36, 48]),
        "claim_count": random.randint(0, 8), "claim_cost_usd": round(max(0, random.gauss(480, 620)), 2),
        "coverage_level": random.choice(["standard", "premium", "mission_critical"]),
        "expiration_risk": round(random.random(), 3),
    } for i in range(n)]


def gen_compliance_logs(n=5000):
    return [{
        "audit_id": str(uuid.uuid4()), "timestamp": rand_time(), "actor_id": f"USR-{random.randint(1000, 9999)}",
        "control": random.choice(["PII_MASKING", "RBAC", "DATA_RETENTION", "MODEL_TRACE", "EXPORT_POLICY"]),
        "resource": random.choice(["contract", "ticket", "invoice", "telemetry", "conversation"]),
        "result": random.choices(["pass", "warning", "fail"], weights=[82, 12, 6])[0],
        "risk_score": round(random.betavariate(1.3, 7), 3), "evidence_uri": f"kb://audit/{uuid.uuid4()}",
    } for _ in range(n)]


def gen_security_events(n=5000):
    return [{
        "security_event_id": str(uuid.uuid4()), "timestamp": rand_time(), "actor_id": f"USR-{random.randint(1000, 9999)}",
        "event_type": random.choice(["login", "failed_login", "export", "prompt_injection", "privilege_change", "api_token_use"]),
        "source_ip": f"10.{random.randint(0, 40)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
        "severity": random.choice(["info", "low", "medium", "high", "critical"]),
        "blocked": random.random() < 0.18, "pii_detected": random.random() < 0.04,
        "rag_security_score": round(random.uniform(0.55, 0.999), 3),
    } for _ in range(n)]


GENERATORS = {
    "printer_telemetry": gen_printer_telemetry,
    "toner_usage": gen_toner_usage,
    "maintenance_logs": gen_maintenance_logs,
    "device_error_logs": gen_error_logs,
    "service_tickets": gen_service_tickets,
    "customer_support_conversations": gen_support_conversations,
    "contracts_slas": gen_contracts,
    "invoice_processing": gen_invoice_processing,
    "employee_workflow_logs": gen_workflow_logs,
    "print_job_history": gen_print_jobs,
    "customer_profiles": gen_customer_profiles,
    "product_catalog": gen_product_catalog,
    "warranty_records": gen_warranty_records,
    "compliance_audit_logs": gen_compliance_logs,
    "security_events": gen_security_events,
}


def main():
    manifest = {}
    for name, fn in GENERATORS.items():
        rows = fn()
        fields = list(rows[0].keys())
        path = write_csv(name, fields, rows)
        manifest[name] = {"path": str(path.relative_to(ROOT)), "records": len(rows), "fields": fields}

    total = sum(item["records"] for item in manifest.values())
    summary = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "dataset_count": len(manifest),
        "total_records": total,
        "datasets": manifest,
        "executive_metrics": {
            "mttr_hours": 14.8,
            "device_uptime_pct": 98.73,
            "cost_savings_usd": 4820000,
            "ticket_resolution_hours": 12.6,
            "churn_risk_pct": 11.4,
            "sla_compliance_pct": 96.8,
            "inventory_health_pct": 91.2,
            "ai_agent_productivity_pct": 68.5,
            "forecast_accuracy_pct": 89.7,
        },
    }
    (DATA_DIR / "manifest.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"total_records": total, "manifest": str(DATA_DIR / "manifest.json")}, indent=2))


if __name__ == "__main__":
    main()

