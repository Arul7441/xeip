from __future__ import annotations

import re


KNOWLEDGE_BASE = {
    "mttr": {
        "value": "14.8 hours",
        "trend": "down 12% vs last quarter",
        "insight": "Field maintenance SLA compliance driving improvement. P1 tickets now resolved avg 6.2h.",
        "recommendation": "Automate parts pre-staging for top 10 error codes to cut MTTR below 10h.",
    },
    "churn": {
        "value": "11.4% at-risk",
        "trend": "stable",
        "insight": "142 accounts flagged by churn model. Top drivers: high ticket volume + negative sentiment.",
        "recommendation": "Assign CSM outreach to top 20 accounts. Offer contract refresh incentive.",
    },
    "toner": {
        "value": "91.2% inventory health",
        "trend": "up 3.1% this month",
        "insight": "Forecast model accuracy at 89.7%. 3 SKUs below reorder threshold.",
        "recommendation": "Trigger procurement for SKU-TN-045, SKU-TN-112, SKU-TN-089 within 48h.",
    },
    "sla": {
        "value": "96.8% compliance",
        "trend": "up 1.2% vs target",
        "insight": "Premium tier at 98.1%. Standard tier at 94.9% — 2 accounts at breach risk.",
        "recommendation": "Pre-emptive escalation for Account-0447 and Account-1203 before month end.",
    },
    "cost": {
        "value": "$4.82M savings",
        "trend": "YTD vs manual operations baseline",
        "insight": "Preventive maintenance automation saving $2.1M. Inventory optimisation $1.4M. Ticket deflection $1.3M.",
        "recommendation": "Expand predictive maintenance to 3 additional device models for incremental $800K savings.",
    },
    "fleet": {
        "value": "98.73% uptime",
        "trend": "best in 18 months",
        "insight": "14 devices currently in warning state. 3 high-risk devices need immediate attention.",
        "recommendation": "Schedule preventive maintenance for XRX-0007, XRX-0019, XRX-0031 this week.",
    },
    "tickets": {
        "value": "12.6h avg resolution",
        "trend": "down 18% QoQ",
        "insight": "AI routing accuracy at 84%. Misrouted tickets average 4.2 reassignments before resolution.",
        "recommendation": "Re-train routing model on Q2 tickets. Focus on fuser/jam disambiguation.",
    },
}

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]

HELP_RESPONSE = {
    "answer": (
        "I'm your XEIP Executive Copilot. I can answer questions about:\n\n"
        "• **Fleet health** — device uptime, failure risk, toner levels\n"
        "• **MTTR** — mean time to repair, maintenance performance\n"
        "• **Churn risk** — at-risk customer accounts\n"
        "• **SLA compliance** — service level performance\n"
        "• **Cost savings** — AI-driven operational savings\n"
        "• **Inventory** — toner and parts forecast\n"
        "• **Tickets** — support resolution performance\n\n"
        "Try asking: *What is our current MTTR?* or *Which devices need attention?*"
    ),
    "confidence": 1.0,
    "topic": "help",
    "sources": ["XEIP Knowledge Base"],
}


def _match_topic(query: str) -> str | None:
    q = query.lower()
    if any(w in q for w in ["mttr", "repair", "maintenance", "fix", "downtime"]):
        return "mttr"
    if any(w in q for w in ["churn", "at-risk", "customer", "account", "retention"]):
        return "churn"
    if any(w in q for w in ["toner", "inventory", "stock", "supply", "cartridge", "sku"]):
        return "toner"
    if any(w in q for w in ["sla", "compliance", "service level", "breach", "contract"]):
        return "sla"
    if any(w in q for w in ["cost", "saving", "roi", "financial", "money", "usd"]):
        return "cost"
    if any(w in q for w in ["fleet", "device", "printer", "uptime", "online", "offline"]):
        return "fleet"
    if any(w in q for w in ["ticket", "support", "resolution", "routing", "escalation"]):
        return "tickets"
    return None


def copilot_query(query: str, role: str = "executive") -> dict:
    q = query.strip().lower()

    if any(g in q for g in GREETINGS):
        return {
            "answer": f"Hello! I'm your XEIP Executive Copilot. How can I help you today? Ask me about fleet health, MTTR, churn risk, SLA compliance, or cost savings.",
            "confidence": 1.0,
            "topic": "greeting",
            "sources": [],
        }

    if any(w in q for w in ["help", "what can you", "what do you", "capabilities"]):
        return HELP_RESPONSE

    topic = _match_topic(query)

    if topic:
        kb = KNOWLEDGE_BASE[topic]
        return {
            "answer": (
                f"**Current status:** {kb['value']}\n\n"
                f"**Trend:** {kb['trend']}\n\n"
                f"**Insight:** {kb['insight']}\n\n"
                f"**Recommendation:** {kb['recommendation']}"
            ),
            "confidence": 0.91,
            "topic": topic,
            "sources": ["XEIP Analytics Engine", "ML Model Output", "Live Telemetry"],
            "governance": {
                "model": "xeip-copilot-v1",
                "policy": "XEIP-COPILOT-001",
                "human_review": "recommended for decisions >$50K impact",
            },
        }

    return {
        "answer": (
            f"I don't have specific data on that query yet. "
            f"I can help with fleet health, MTTR, churn risk, SLA compliance, cost savings, inventory, and ticket performance. "
            f"Try rephrasing or ask 'help' to see all topics."
        ),
        "confidence": 0.3,
        "topic": "unknown",
        "sources": [],
        "suggestion": "Try: 'What is our MTTR?', 'Show churn risk', 'Fleet status'",
    }
