from __future__ import annotations
import csv, pathlib, re
from .observability import audit_event, system_trace
from .schemas import RagQuery
from .security import User, mask_pii, validate_prompt

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

KNOWLEDGE = [
    {"source":"Maintenance Guide MG-ALTA-2026","text":"High temperature plus repeated 077-900 faults indicates fuser stress. Replace fuser if calibration fails twice.","domain":"maintenance","classification":"internal","required_permission":"read:operations"},
    {"source":"SOP SUP-114 Ticket Escalation","text":"P1 support cases must be triaged in 15 minutes and escalated when remote recovery fails.","domain":"support","classification":"internal","required_permission":"read:support"},
    {"source":"Contract Policy SLA-22","text":"Mission critical contracts require 99.5 percent uptime and four hour onsite response.","domain":"contract","classification":"confidential","required_permission":"contract:read"},
    {"source":"Security Procedure SEC-RAG-9","text":"Retrieved context must be permission filtered, PII masked, and checked for prompt injection instructions.","domain":"security","classification":"restricted","required_permission":"read:audit"},
]

def _extract_device_id(query):
    m = re.search(r"XRX-\d+", query, re.IGNORECASE)
    return m.group(0).upper() if m else None

def _diagnose_device(device_id):
    tel  = [r for r in TELEMETRY   if r.get("device_id","").upper() == device_id]
    errs = [r for r in ERRORS      if r.get("device_id","").upper() == device_id]
    mnt  = [r for r in MAINTENANCE if r.get("device_id","").upper() == device_id]
    tix  = [r for r in TICKETS     if r.get("device_id","").upper() == device_id]

    if not tel and not errs:
        return {"found": False, "device_id": device_id}

    latest   = sorted(tel, key=lambda r: r.get("timestamp",""), reverse=True)[0] if tel else {}
    last_err = sorted(errs, key=lambda r: r.get("timestamp",""), reverse=True)[0] if errs else {}
    last_mnt = sorted(mnt, key=lambda r: r.get("timestamp",""), reverse=True)[0] if mnt else {}

    temp=latest.get("temperature_c","N/A"); toner=latest.get("toner_level_pct","N/A")
    err_freq=latest.get("error_frequency","N/A"); anomaly=latest.get("anomaly_flag","False")
    model=latest.get("model","Unknown"); customer=latest.get("customer","Unknown"); region=latest.get("region","Unknown")
    err_code=last_err.get("error_code","none"); err_sub=last_err.get("subsystem","")
    err_sev=last_err.get("severity",""); recovered=last_err.get("auto_recovered","True")
    mnt_type=last_mnt.get("maintenance_type","none"); mnt_parts=last_mnt.get("parts_replaced","none")
    mnt_notes=last_mnt.get("notes",""); mnt_date=last_mnt.get("timestamp","")[:10] if last_mnt else "never"

    issues=[]; actions=[]; severity="low"

    try:
        t=float(temp)
        if t>75: issues.append(f"CRITICAL: Temperature {t}C — overheating, fuser damage risk"); actions.append("Power off immediately, call technician"); severity="critical"
        elif t>55: issues.append(f"WARNING: Temperature {t}C — above normal"); actions.append("Check ventilation, schedule inspection"); severity="high"
    except: pass

    try:
        tn=float(toner)
        if tn<10: issues.append(f"CRITICAL: Toner {tn}% — will stop printing imminently"); actions.append("Replace toner cartridge immediately"); severity="critical"
        elif tn<20: issues.append(f"WARNING: Toner {tn}% — order replacement now"); actions.append("Order toner (3-5 day lead time)")
    except: pass

    if err_code and err_code!="none":
        rec="auto-recovered" if recovered=="True" else "DID NOT recover — manual fix required"
        issues.append(f"Last error: {err_code} on {err_sub} ({err_sev}, {rec})")
        if recovered!="True": actions.append(f"Manual fix needed for {err_code}"); severity="critical"

    if err_code=="077-900" or (err_freq and str(err_freq).isdigit() and int(err_freq)>15):
        issues.append("Fuser stress pattern — matches MG-ALTA-2026 criteria"); actions.append("Schedule fuser replacement if calibration fails again")

    if anomaly=="True": issues.append("Anomaly flag active — unusual pattern"); severity="high"
    if not issues: issues.append("No critical issues in latest telemetry"); actions.append("Device appears operational")

    return {"found":True,"device_id":device_id,"model":model,"customer":customer,"region":region,
            "temperature_c":temp,"toner_pct":toner,"error_frequency":err_freq,
            "last_error_code":err_code,"last_error_subsystem":err_sub,"last_error_severity":err_sev,
            "auto_recovered":recovered,"last_maintenance_date":mnt_date,"last_maintenance_type":mnt_type,
            "parts_last_replaced":mnt_parts,"maintenance_notes":mnt_notes,"open_tickets":len(tix),
            "issues":issues,"recommended_actions":actions,"severity":severity,
            "data_sources":["printer_telemetry.csv","device_error_logs.csv","maintenance_logs.csv","service_tickets.csv"]}

def _format_diagnosis(d):
    if not d["found"]: return f"Device {d['device_id']} not found. Please check the device ID."
    lines=[
        f"Device {d['device_id']} — {d['model']}",
        f"Customer: {d['customer']} | Region: {d['region']}","",
        "Current Status:",
        f"  Temperature: {d['temperature_c']}C",
        f"  Toner Level: {d['toner_pct']}%",
        f"  Error Frequency: {d['error_frequency']}",
        f"  Last Error: {d['last_error_code']} ({d['last_error_subsystem']}, {d['last_error_severity']})",
        f"  Auto-recovered: {d['auto_recovered']}",
        f"  Last Maintenance: {d['last_maintenance_date']} ({d['last_maintenance_type']})",
        f"  Parts Replaced: {d['parts_last_replaced']}",
        f"  Open Tickets: {d['open_tickets']}","",
        "Diagnosed Issues:",
    ]
    for i in d["issues"]: lines.append(f"  * {i}")
    lines.append(""); lines.append("Recommended Actions:")
    for a in d["recommended_actions"]: lines.append(f"  -> {a}")
    return "\n".join(lines)

def _search_by_symptom(query):
    q=query.lower(); keywords=[]
    if any(w in q for w in ["not turning on","won't turn on","dead","no power","power"]): keywords=["power","firmware","boot"]
    elif any(w in q for w in ["not printing","won't print","no print","blank page"]): keywords=["toner","fuser","jam","print"]
    elif any(w in q for w in ["paper jam","jam","stuck","feed"]): keywords=["paper jam","jam","feed"]
    elif any(w in q for w in ["scan","scanning","email"]): keywords=["scan","email"]
    elif any(w in q for w in ["slow","taking long","delay"]): keywords=["network","firmware"]
    elif any(w in q for w in ["toner","ink","cartridge"]): keywords=["toner"]
    elif any(w in q for w in ["network","wifi","connect","offline"]): keywords=["network","connectivity"]
    elif any(w in q for w in ["error","fault","code"]): keywords=["error"]
    if not keywords: return ""

    matches=[t for t in TICKETS if any(kw in t.get("summary","").lower() for kw in keywords)]
    err_matches=[e for e in ERRORS if any(kw in e.get("subsystem","").lower() for kw in keywords)]
    if not matches and not err_matches: return ""

    lines=[f"Found {len(matches)} similar cases in service history:"]
    for t in matches[:3]: lines.append(f"  {t['device_id']} ({t['customer']}): {t['summary']} — resolved in {t['resolution_hours']}h")
    if err_matches:
        codes=list({e['error_code'] for e in err_matches[:5]})
        lines.append(f"\nCommon error codes: {', '.join(codes)}")

    if any(w in q for w in ["not turning on","power","dead"]): lines.append("\nFix: Check power cable, firmware reset. Escalate to P1 if unresponsive after 2 min.")
    elif any(w in q for w in ["not printing","won't print"]): lines.append("\nFix: Check toner level, clear paper path, verify driver. Most common fix: toner replacement.")
    elif any(w in q for w in ["jam","stuck"]): lines.append("\nFix: Open all access doors, remove paper carefully, check tray alignment.")
    elif any(w in q for w in ["scan"]): lines.append("\nFix: Restart scan service, check SMTP/network settings.")
    return "\n".join(lines)

def answer_with_sources(request: RagQuery, user: User):
    controls=["prompt_injection_scan","rbac_metadata_filter","pii_masking","citation_required"]
    validation=validate_prompt(request.query)

    if not validation["allowed"]:
        audit=audit_event(request_id=request.governance.request_id,tenant_id=request.governance.tenant_id,
            actor=user.subject,action="rag.query",resource="knowledge_base",decision="blocked",
            controls=controls,risk_score=1-validation["score"],evidence=["Security Procedure SEC-RAG-9"])
        return {"answer":"BLOCKED: Prompt injection detected. Logged.","confidence":0.99,
                "sources":["Security Procedure SEC-RAG-9"],"risk_factors":validation["risk_flags"],
                "audit":audit,"trace":system_trace(request.governance.request_id,controls)}

    query=request.query

    # 1. Device ID lookup
    device_id=_extract_device_id(query)
    if device_id:
        diag=_diagnose_device(device_id)
        answer=_format_diagnosis(diag)
        audit=audit_event(request_id=request.governance.request_id,tenant_id=request.governance.tenant_id,
            actor=user.subject,action="rag.query",resource="knowledge_base",decision="answered",
            controls=controls,risk_score=0.12,evidence=diag.get("data_sources",[]))
        return {"answer":mask_pii(answer),"confidence":0.95 if diag["found"] else 0.5,
                "sources":diag.get("data_sources",[]),"device_diagnosis":diag,
                "reasoning":"Direct lookup across telemetry, errors, maintenance, and tickets.",
                "risk_factors":[],"audit":audit,"trace":system_trace(request.governance.request_id,controls)}

    # 2. Symptom search
    symptom=_search_by_symptom(query)
    if symptom:
        audit=audit_event(request_id=request.governance.request_id,tenant_id=request.governance.tenant_id,
            actor=user.subject,action="rag.query",resource="knowledge_base",decision="answered",
            controls=controls,risk_score=0.15,evidence=["service_tickets.csv","device_error_logs.csv"])
        return {"answer":symptom,"confidence":0.82,"sources":["service_tickets.csv","device_error_logs.csv"],
                "reasoning":"Symptom search across 5,001 tickets and error logs.","risk_factors":[],
                "audit":audit,"trace":system_trace(request.governance.request_id,controls)}

    # 3. Static knowledge docs
    terms=set(query.lower().split()); scored=[]
    for doc in KNOWLEDGE:
        if doc["required_permission"] not in user.permissions and "read:all" not in user.permissions: continue
        score=sum(1 for t in terms if t in doc["text"].lower() or t in doc["domain"])
        if score: scored.append((score,doc))
    selected=[doc for _,doc in sorted(scored,key=lambda x:x[0],reverse=True)[:3]]
    if selected:
        audit=audit_event(request_id=request.governance.request_id,tenant_id=request.governance.tenant_id,
            actor=user.subject,action="rag.query",resource="knowledge_base",decision="answered",
            controls=controls,risk_score=0.18,evidence=[d["source"] for d in selected])
        return {"answer":mask_pii("Based on enterprise knowledge: "+" ".join(d["text"] for d in selected)),
                "confidence":round(min(0.94,0.62+len(selected)*0.11),2),"sources":[d["source"] for d in selected],
                "reasoning":"Matched policy documents.","risk_factors":[],
                "audit":audit,"trace":system_trace(request.governance.request_id,controls)}

    # 4. Nothing found
    audit=audit_event(request_id=request.governance.request_id,tenant_id=request.governance.tenant_id,
        actor=user.subject,action="rag.query",resource="knowledge_base",decision="abstained",
        controls=controls,risk_score=0.68)
    return {"answer":"No matching records found. Try: device ID (e.g. XRX-100000), or describe symptom: 'not turning on', 'not printing', 'paper jam', 'scan broken', 'toner low'.","confidence":0.2,"sources":[],"risk_factors":["insufficient evidence"],"audit":audit,"trace":system_trace(request.governance.request_id,controls)}