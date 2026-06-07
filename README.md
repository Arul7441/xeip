# Xerox Enterprise Intelligence Platform

XEIP is a production-shaped enterprise AI operating system demo for document operations, printer telemetry, predictive maintenance, contract intelligence, inventory automation, support, compliance, and executive decision-making.

This repository includes:

- Synthetic enterprise data generation for 15 domains and 75,000+ records
- FastAPI backend with agent, RAG, ML, security, audit, workflow, and executive endpoints
- Next.js-style frontend source and a standalone executive dashboard artifact
- Architecture, database, agent, RAG, security, deployment, API, benchmark, and demo documentation
- Principal-engineer gap analysis and enterprise-readiness checklist
- Focused tests for data generation, agent routing, and API health

## Quick Start

Generate all datasets and the standalone dashboard:

```bash
python3 scripts/generate_enterprise_data.py
python3 scripts/build_dashboard.py
```

Run the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open the generated dashboard:

```bash
open ../../outputs/xeip-executive-dashboard.html
```

## Repository Map

- `backend/app`: API, agents, RAG, ML, security, workflows
- `scripts`: data generation and dashboard build scripts
- `data`: generated CSV datasets and summary metrics
- `docs`: architecture, schemas, diagrams, guides, benchmarks, demos
- `frontend`: Next.js/Tailwind source for a productized UI
- `deploy`: Docker and Kubernetes deployment assets

## Enterprise Hardening Added

- Deny-by-default authentication with role permissions
- Tenant-scoped governance envelopes on autonomous requests
- Typed API inputs with feature bounds and business-impact metadata
- RAG prompt-injection gating, metadata ACL filtering, citation requirement, and abstention
- Model cards, drift scores, intended-use limits, and monitoring metadata
- Workflow approval thresholds for restricted or high-value actions
- Security headers, rate limiting, audit event structure, and data-quality profiling
- Non-root container, Kubernetes resources, probes, HPA, PDB, and NetworkPolicy
