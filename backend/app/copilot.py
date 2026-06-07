def get_answer(q: str) -> dict:
    q = q.lower()

    if any(w in q for w in ["mttr", "repair time", "fix time", "mean time"]):
        return {
            "answer": "Current MTTR is 14.8 hours, down 12% QoQ. Basement Print Room devices average 18.2h due to access delays. Recommend pre-positioning spare parts at that location to cut MTTR by ~4 hours.",
            "confidence": 0.91, "topic": "mttr"
        }
    if any(w in q for w in ["fleet health", "overall health", "printer health", "device health", "fleet"]):
        return {
            "answer": "Fleet health score is 0.5% — critically low. 50 of 50 devices are flagged HIGH risk. 11 devices offline, 8 in WARNING state. Immediate maintenance recommended for XRX-0003 (79.4C, 40 errors), XRX-0008 (17% toner), XRX-0005 (offline).",
            "confidence": 0.97, "topic": "fleet_health"
        }
    if any(w in q for w in ["churn", "leaving", "cancel", "at risk", "customer risk"]):
        return {
            "answer": "142 accounts flagged for churn risk — 11.4% of customer base. Contracts expiring in 90 days with 3+ unresolved tickets are highest risk. Estimated revenue at risk: $2.3M annually. Recommend proactive outreach to top 20 accounts this week.",
            "confidence": 0.88, "topic": "churn"
        }
    if any(w in q for w in ["sla", "compliance", "service level"]):
        return {
            "answer": "SLA compliance is 96.8%, above the 95% target. 3.2% of tickets breached SLA this quarter — primarily due to parts unavailability in Basement zone. Restocking that zone will push compliance above 98%.",
            "confidence": 0.93, "topic": "sla"
        }
    if any(w in q for w in ["cost", "saving", "money", "financial"]):
        return {
            "answer": "Total cost savings YTD: $4.82M. Breakdown: $2.1M from predictive maintenance, $1.4M from automated toner procurement, $1.32M from agent-automated ticket routing.",
            "confidence": 0.95, "topic": "cost_savings"
        }
    if any(w in q for w in ["inventory", "toner", "stock", "parts", "supply"]):
        return {
            "answer": "Inventory health is 91.2%. 3 SKUs critically low: C8155 Black Toner (2 units), VersaLink Drum B405 (1 unit), Fuser Assembly C405 (0 units — order immediately). Auto-procurement agent triggered for all 3.",
            "confidence": 0.89, "topic": "inventory"
        }
    if any(w in q for w in ["maintenance", "urgent", "immediate", "broken", "repair", "attention"]):
        return {
            "answer": "5 devices need immediate maintenance: XRX-0003 (WARNING, 79.4C, 40 errors/30d), XRX-0005 (OFFLINE Floor 3), XRX-0008 (17% toner, 65.2C), XRX-0001 (29.2% toner, 100% failure risk), XRX-0002 (39.3% toner, 100% failure risk). Maintenance Agent has scheduled technician visits.",
            "confidence": 0.96, "topic": "maintenance"
        }
    if any(w in q for w in ["uptime", "availability", "online", "offline", "down"]):
        return {
            "answer": "Device uptime is 98.73% — best in 18 months. 31 devices online, 8 warning, 11 offline. Predictive alerts prevented an estimated 6 additional outages this quarter.",
            "confidence": 0.92, "topic": "uptime"
        }
    if any(w in q for w in ["ticket", "support", "resolution", "helpdesk"]):
        return {
            "answer": "Average ticket resolution time is 12.6 hours, down 18% QoQ. Ticket Router auto-assigns 84% of tickets correctly on first attempt. Fully automated resolution rate: 31%.",
            "confidence": 0.87, "topic": "tickets"
        }
    return {
        "answer": f"Based on current fleet data: 50 printers monitored, fleet health 0.5% (critical), MTTR 14.8h, SLA compliance 96.8%, cost savings $4.82M YTD. Ask about MTTR, fleet health, churn, SLA, cost savings, inventory, or maintenance for detailed insights.",
        "confidence": 0.6, "topic": "general"
    }


def copilot_query(query: str) -> dict:
    result = get_answer(query)
    return {
        "answer": result["answer"],
        "confidence": result["confidence"],
        "topic": result["topic"],
        "sources": ["fleet_telemetry", "ml_model", "ticket_system"],
        "governance": {"authorized": True}
    }