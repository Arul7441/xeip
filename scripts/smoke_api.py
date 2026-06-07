"""
smoke_api.py — XEIP API smoke test
Run from: C:\Users\KAIPULLA\Desktop\xeip\
Command:  python scripts\smoke_api.py
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://localhost:8080"

TOKENS = {
    "executive": "Bearer demo.demo-tenant.executive",
    "operations": "Bearer demo.demo-tenant.operations",
}

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"

results = []


def call(method, path, token_role="executive", body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": TOKENS[token_role],
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as ex:
        return 0, {"error": str(ex)}


def test(label, method, path, token_role="executive", body=None, expect_status=200, check_key=None):
    status, resp = call(method, path, token_role, body)
    ok = status == expect_status
    if ok and check_key:
        ok = check_key in resp
    tag = PASS if ok else FAIL
    results.append(ok)
    detail = f"  status={status}"
    if check_key:
        detail += f"  key='{check_key}' {'found' if check_key in resp else 'MISSING'}"
    print(f"{tag}  [{method:4s}] {path:<40s}{detail}")


print("\n=== XEIP API Smoke Test ===\n")

# Core
test("Health check",            "GET",  "/health",            check_key="status")
test("Executive metrics",       "GET",  "/metrics/executive", check_key="mttr_hours")

# Fleet (NEW)
test("Fleet live",              "GET",  "/fleet/live?limit=5", token_role="operations", check_key="devices")
test("Fleet stats",             "GET",  "/fleet/stats",        token_role="operations", check_key="total_fleet")
test("Fleet alert filter",      "GET",  "/fleet/live?alert=high", token_role="operations", check_key="devices")

# Copilot (NEW)
test("Copilot - MTTR query",   "POST", "/copilot/query", body={
    "query": "What is our current MTTR?",
    "governance": {"request_id": "smoke-001", "tenant_id": "demo-tenant"}
}, check_key="answer")

test("Copilot - fleet query",  "POST", "/copilot/query", body={
    "query": "Show me fleet status",
    "governance": {"request_id": "smoke-002", "tenant_id": "demo-tenant"}
}, check_key="answer")

# ML endpoints
test("ML failure prediction",  "POST", "/ml/failure", token_role="operations", body={
    "temperature": 65, "usage_count": 120000, "error_frequency": 12,
    "maintenance_history": 0.7, "toner_level": 35
}, check_key="failure_probability")

test("ML churn prediction",    "POST", "/ml/churn", token_role="operations", body={
    "ticket_count": 45, "usage_trend": -0.3, "support_sentiment": -0.5, "contract_age": 24
}, check_key="churn_probability")

test("ML inventory forecast",  "POST", "/ml/inventory", token_role="operations", body={
    "daily_usage": [12, 14, 13, 15, 11, 14, 13],
    "horizon_days": 30, "stock_on_hand": 200
}, check_key="forecast_units")

test("Ticket routing",         "POST", "/route-ticket", token_role="operations", body={
    "summary": "Fuser unit error 077-900 device offline floor 2",
    "priority": "P2", "sentiment": -0.6, "device_error_count": 8
}, check_key="ticket_queue")

test("Anomaly detection",      "POST", "/detect-anomaly", token_role="operations", body={
    "failed_login_count": 15, "unusual_location": True,
    "after_hours_access": True, "data_volume_mb": 500
}, check_key="anomaly_probability")

# Agents
test("Agent orchestrate",      "POST", "/agents/orchestrate", body={
    "objective": "low toner procurement for fleet",
    "payload": {"daily_usage": [12, 14, 13], "stock_on_hand": 10},
    "governance": {"request_id": "smoke-003", "tenant_id": "demo-tenant", "business_impact_usd": 2000}
}, check_key="agents_invoked")

# Auth check — wrong role should get 403
test("Auth enforcement",       "GET",  "/data-quality", token_role="operations", expect_status=403)

# Summary
total = len(results)
passed = sum(results)
failed = total - passed
print(f"\n{'='*45}")
print(f"  Results: {passed}/{total} passed  ({failed} failed)")
print(f"{'='*45}\n")

if failed > 0:
    sys.exit(1)
