"""Expert AI Copilot — answers from the real CSV datasets, not hardcoded demo text.

Resolution order for each query:
  1. Device lookup   -> "what's wrong with XRX-100000"
  2. Customer lookup -> "how is Vertex Legal doing"
  3. Live metric     -> mttr / sla / churn / cost / inventory / fleet / uptime / tickets
  4. Keyword fallback (only when nothing in the data matches)

All numbers in the metric answers are computed from the CSVs at import time.
"""
from __future__ import annotations
import csv, pathlib, re, statistics

BASE = pathlib.Path(__file__).parent.parent.parent
DATA = BASE / "data"


def _load(name):
    p = DATA / name
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


TELEMETRY   = _load("printer_telemetry.csv")
ERRORS      = _load("device_error_logs.csv")
MAINTENANCE = _load("maintenance_logs.csv")
TICKETS     = _load("service_tickets.csv")
CUSTOMERS   = _load("customer_profiles.csv")
CONTRACTS   = _load("contracts_slas.csv")
CATALOG     = _load("product_catalog.csv")


def _nums(rows, col):
    out = []
    for r in rows:
        v = r.get(col, "")
        if v not in ("", None):
            try:
                out.append(float(v))
            except ValueError:
                pass
    return out


def _avg(rows, col, default=0.0):
    vals = _nums(rows, col)
    return statistics.mean(vals) if vals else default


# --- Aggregates computed once from the real data ---------------------------
def _build_metrics():
    device_ids = {r.get("device_id", "") for r in TELEMETRY if r.get("device_id")}
    anomalies = sum(1 for r in TELEMETRY if r.get("anomaly_flag") == "True")
    telemetry_n = len(TELEMETRY) or 1

    downtime_min = _nums(MAINTENANCE, "downtime_minutes")
    mttr_hours = (statistics.mean(downtime_min) / 60) if downtime_min else 0.0

    sla_flags = [r.get("sla_met") for r in TICKETS if r.get("sla_met") in ("True", "False")]
    sla_pct = (100 * sla_flags.count("True") / len(sla_flags)) if sla_flags else 0.0

    churn_vals = _nums(CUSTOMERS, "churn_probability")
    at_risk = [r for r in CUSTOMERS if (r.get("churn_probability") or "0") not in ("",) and _safe(r["churn_probability"]) >= 0.5]
    acv_at_risk = sum(_safe(r.get("annual_contract_value", 0)) for r in at_risk)

    maint_cost = sum(_nums(MAINTENANCE, "cost_usd"))

    active = [r for r in CATALOG if r.get("active") == "True"]
    below_reorder = [r for r in active if _safe(r.get("stock_on_hand", 0)) < _safe(r.get("reorder_point", 0))]

    res_hours = _nums(TICKETS, "resolution_hours")
    escalated = sum(1 for r in TICKETS if r.get("escalated") == "True")
    p1 = sum(1 for r in TICKETS if r.get("priority") == "P1")

    return {
        "device_count": len(device_ids),
        "telemetry_events": len(TELEMETRY),
        "anomaly_pct": round(100 * anomalies / telemetry_n, 1),
        "avg_toner": round(_avg(TELEMETRY, "toner_level_pct"), 1),
        "avg_temp": round(_avg(TELEMETRY, "temperature_c"), 1),
        "mttr_hours": round(mttr_hours, 1),
        "sla_pct": round(sla_pct, 1),
        "avg_sla_uptime": round(_avg(CONTRACTS, "sla_uptime_pct"), 2),
        "churn_avg": round(100 * (statistics.mean(churn_vals) if churn_vals else 0), 1),
        "churn_count": len(at_risk),
        "customer_count": len(CUSTOMERS),
        "acv_at_risk": round(acv_at_risk),
        "maint_cost": round(maint_cost),
        "maint_jobs": len(MAINTENANCE),
        "active_skus": len(active),
        "below_reorder": len(below_reorder),
        "low_stock_skus": [r.get("product_name", r.get("sku", "?")) for r in below_reorder[:5]],
        "avg_resolution": round(statistics.mean(res_hours), 1) if res_hours else 0.0,
        "escalated_pct": round(100 * escalated / (len(TICKETS) or 1), 1),
        "p1_tickets": p1,
        "ticket_count": len(TICKETS),
    }


def _safe(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


M = _build_metrics()
SOURCES_ALL = ["printer_telemetry.csv", "service_tickets.csv", "customer_profiles.csv",
               "contracts_slas.csv", "maintenance_logs.csv", "product_catalog.csv"]

# Known customer names (longest first so multi-word names match before substrings)
CUSTOMER_NAMES = sorted({r.get("customer", "") for r in CUSTOMERS if r.get("customer")},
                        key=len, reverse=True)


# --- Device diagnosis ------------------------------------------------------
def _diagnose_device(device_id):
    tel  = [r for r in TELEMETRY   if r.get("device_id", "").upper() == device_id]
    errs = [r for r in ERRORS      if r.get("device_id", "").upper() == device_id]
    mnt  = [r for r in MAINTENANCE if r.get("device_id", "").upper() == device_id]
    tix  = [r for r in TICKETS     if r.get("device_id", "").upper() == device_id]
    if not tel and not errs:
        return None

    latest   = sorted(tel,  key=lambda r: r.get("timestamp", ""), reverse=True)[0] if tel else {}
    last_err = sorted(errs, key=lambda r: r.get("timestamp", ""), reverse=True)[0] if errs else {}
    last_mnt = sorted(mnt,  key=lambda r: r.get("timestamp", ""), reverse=True)[0] if mnt else {}

    temp = latest.get("temperature_c", "N/A"); toner = latest.get("toner_level_pct", "N/A")
    issues, actions = [], []
    if temp not in ("", "N/A") and _safe(temp) > 75:
        issues.append(f"Temperature {temp}C — overheating / fuser damage risk")
        actions.append("Power off and dispatch technician")
    elif temp not in ("", "N/A") and _safe(temp) > 55:
        issues.append(f"Temperature {temp}C — above normal")
        actions.append("Check ventilation")
    if toner not in ("", "N/A") and _safe(toner) < 10:
        issues.append(f"Toner {toner}% — will stop printing soon"); actions.append("Replace toner now")
    elif toner not in ("", "N/A") and _safe(toner) < 20:
        issues.append(f"Toner {toner}% — order replacement"); actions.append("Order toner (3-5d lead)")
    if last_err.get("error_code"):
        rec = "auto-recovered" if last_err.get("auto_recovered") == "True" else "DID NOT recover — manual fix"
        issues.append(f"Last error {last_err['error_code']} on {last_err.get('subsystem','')} ({rec})")
    if not issues:
        issues.append("No critical issues in latest telemetry"); actions.append("Device operational")

    lines = [
        f"Device {device_id} - {latest.get('model','Unknown')}",
        f"Customer: {latest.get('customer','Unknown')} | Region: {latest.get('region','Unknown')}",
        f"Temperature: {temp}C | Toner: {toner}% | Error freq: {latest.get('error_frequency','N/A')}",
        f"Last maintenance: {last_mnt.get('timestamp','never')[:10]} ({last_mnt.get('maintenance_type','none')})",
        f"Open tickets: {len(tix)}",
        "",
        "Issues: " + "; ".join(issues),
        "Recommended: " + "; ".join(actions),
    ]
    return "\n".join(lines)


# --- Customer summary ------------------------------------------------------
def _summarize_customer(name):
    prof = next((r for r in CUSTOMERS if r.get("customer", "").lower() == name.lower()), None)
    devices = {r.get("device_id") for r in TELEMETRY if r.get("customer", "").lower() == name.lower()}
    tix = [r for r in TICKETS if r.get("customer", "").lower() == name.lower()]
    contract = next((r for r in CONTRACTS if r.get("customer", "").lower() == name.lower()), None)

    res = _nums(tix, "resolution_hours")
    escal = sum(1 for r in tix if r.get("escalated") == "True")
    lines = [f"Customer: {name}"]
    if prof:
        churn = round(_safe(prof.get("churn_probability")) * 100, 1)
        lines.append(f"Industry: {prof.get('industry','?')} | Region: {prof.get('region','?')} | "
                     f"Fleet: {prof.get('fleet_size','?')} devices")
        lines.append(f"Annual contract value: ${_safe(prof.get('annual_contract_value')):,.0f}")
        lines.append(f"Churn probability: {churn}%  |  Support sentiment: {prof.get('support_sentiment','?')}  |  "
                     f"Tickets (90d): {prof.get('ticket_count_90d','?')}")
        if churn >= 50:
            lines.append("  >> HIGH CHURN RISK — recommend customer-success outreach this week")
    lines.append(f"Devices seen in telemetry: {len(devices)}")
    if tix:
        avg_res = round(statistics.mean(res), 1) if res else 0
        lines.append(f"Service tickets: {len(tix)} | avg resolution {avg_res}h | {escal} escalated")
    if contract:
        lines.append(f"Contract: {contract.get('sla_uptime_pct','?')}% SLA uptime | "
                     f"${_safe(contract.get('monthly_value_usd')):,.0f}/mo | "
                     f"renewal risk {round(_safe(contract.get('renewal_risk'))*100)}% | "
                     f"{contract.get('violation_count','0')} violations")
    if not prof and not tix and not contract:
        return None
    return "\n".join(lines)


# --- Metric answers (computed from real data) ------------------------------
def _metric_answer(q):
    if any(w in q for w in ["mttr", "repair time", "fix time", "mean time", "downtime"]):
        return (f"MTTR is {M['mttr_hours']} hours, computed from {M['maint_jobs']:,} maintenance records. "
                f"Average ticket resolution time is {M['avg_resolution']}h across {M['ticket_count']:,} tickets."), 0.93, "mttr"
    if any(w in q for w in ["sla", "compliance", "service level"]):
        return (f"SLA compliance is {M['sla_pct']}% of {M['ticket_count']:,} tickets met SLA. "
                f"Contracted average uptime is {M['avg_sla_uptime']}%."), 0.93, "sla"
    if any(w in q for w in ["churn", "leaving", "cancel", "at risk", "retention"]):
        return (f"{M['churn_count']:,} of {M['customer_count']:,} customers are high churn risk "
                f"(probability >= 50%). Average churn probability is {M['churn_avg']}%. "
                f"Annual contract value at risk: ${M['acv_at_risk']:,}."), 0.9, "churn"
    if any(w in q for w in ["cost", "saving", "money", "spend", "financial"]):
        return (f"Total maintenance spend across {M['maint_jobs']:,} jobs is ${M['maint_cost']:,}. "
                f"Predictive maintenance and automated routing reduce this by avoiding unplanned downtime."), 0.88, "cost"
    if any(w in q for w in ["inventory", "toner", "stock", "parts", "supply", "reorder"]):
        low = ", ".join(M["low_stock_skus"]) or "none"
        return (f"{M['active_skus']:,} active SKUs. {M['below_reorder']} are below reorder point. "
                f"Avg fleet toner level is {M['avg_toner']}%. Low stock: {low}."), 0.9, "inventory"
    if any(w in q for w in ["fleet", "device health", "printer health", "overall health"]):
        return (f"Fleet has {M['device_count']:,} devices across {M['telemetry_events']:,} telemetry events. "
                f"{M['anomaly_pct']}% of readings flagged anomalous. "
                f"Avg temperature {M['avg_temp']}C, avg toner {M['avg_toner']}%."), 0.92, "fleet"
    if any(w in q for w in ["uptime", "availability", "online", "offline"]):
        return (f"Contracted average uptime is {M['avg_sla_uptime']}%. "
                f"{M['anomaly_pct']}% of telemetry readings are anomalous across {M['device_count']:,} devices."), 0.9, "uptime"
    if any(w in q for w in ["ticket", "support", "resolution", "helpdesk", "escalat"]):
        return (f"{M['ticket_count']:,} tickets: avg resolution {M['avg_resolution']}h, "
                f"{M['escalated_pct']}% escalated, {M['p1_tickets']} P1. SLA met on {M['sla_pct']}%."), 0.9, "tickets"
    return None


# --- Entry point (signature unchanged: main.py calls copilot_query(query)) -
def copilot_query(query: str) -> dict:
    q = (query or "").lower().strip()

    # 1. Device lookup
    m = re.search(r"xrx-\d+", q)
    if m:
        diag = _diagnose_device(m.group(0).upper())
        if diag:
            return {"answer": diag, "confidence": 0.95, "topic": "device",
                    "sources": ["printer_telemetry.csv", "device_error_logs.csv",
                                "maintenance_logs.csv", "service_tickets.csv"],
                    "governance": {"authorized": True}}
        return {"answer": f"Device {m.group(0).upper()} not found in telemetry or error logs. "
                          f"Check the device ID (real IDs look like XRX-100000).",
                "confidence": 0.4, "topic": "device", "sources": ["printer_telemetry.csv"],
                "governance": {"authorized": True}}

    # 2. Customer lookup
    for name in CUSTOMER_NAMES:
        if name and name.lower() in q:
            summary = _summarize_customer(name)
            if summary:
                return {"answer": summary, "confidence": 0.92, "topic": "customer",
                        "sources": ["customer_profiles.csv", "service_tickets.csv",
                                    "contracts_slas.csv", "printer_telemetry.csv"],
                        "governance": {"authorized": True}}

    # 3. Live metric
    metric = _metric_answer(q)
    if metric:
        answer, conf, topic = metric
        return {"answer": answer, "confidence": conf, "topic": topic,
                "sources": SOURCES_ALL, "governance": {"authorized": True}}

    # 4. Fallback
    return {"answer": (f"I can answer from live data on {M['device_count']:,} devices, "
                       f"{M['customer_count']:,} customers, and {M['ticket_count']:,} tickets. "
                       f"Ask about a device (e.g. XRX-100000), a customer (e.g. Vertex Legal), "
                       f"or a metric: MTTR, SLA, churn, cost, inventory, fleet, uptime, tickets."),
            "confidence": 0.55, "topic": "general",
            "sources": SOURCES_ALL, "governance": {"authorized": True}}
