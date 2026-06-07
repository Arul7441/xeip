# Xerox Enterprise Intelligence Platform

XEIP is a production-shaped enterprise AI operating system demo for document operations, printer telemetry, predictive maintenance, contract intelligence, inventory automation, support, compliance, and executive decision-making.

This repository includes:

- Synthetic enterprise data generation for 15 domains and 75,000+ records
- FastAPI backend with agent, RAG, ML, security, audit, workflow, and executive endpoints
- Next.js-style frontend source and a standalone executive dashboard artifact
- Architecture, database, agent, RAG, security, deployment, API, and demo documentation
- PostgreSQL schema, Qdrant-ready RAG layout, Docker Compose, Kubernetes, Helm, and Terraform assets
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

Test key APIs:

```bash
curl http://localhost:8080/health

curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo.demo-tenant.executive" \
  -d '{"objective":"low toner procurement for fleet","payload":{"daily_usage":[12,14,13],"stock_on_hand":10},"governance":{"request_id":"req-00001","tenant_id":"demo-tenant","business_impact_usd":2000}}'
```

Open the generated dashboard:

```bash
open ../../outputs/xeip-executive-dashboard.html
```

Run the full local stack with PostgreSQL and Qdrant:

```bash
docker compose up --build
```

## Repository Map

- `backend/app`: API, agents, RAG, ML, security, workflows
- `rag`: embeddings, retriever, reranker, and generator components
- `scripts`: data generation and dashboard build scripts
- `data`: generated CSV datasets and summary metrics
- `database`: PostgreSQL schema
- `docs`: architecture, schemas, diagrams, guides, benchmarks, demos
- `frontend`: Next.js/Tailwind source for a productized UI
- `deploy`: Docker and Kubernetes deployment assets
- `helm`: Helm chart
- `terraform`: Terraform deployment skeleton

## Enterprise Hardening Added

- Deny-by-default authentication with role permissions and optional signed JWT validation
- Tenant-scoped governance envelopes on autonomous requests
- Typed API inputs with feature bounds and business-impact metadata
- RAG prompt-injection gating, metadata ACL filtering, citation requirement, and abstention
- Model cards, drift scores, intended-use limits, and monitoring metadata
- Workflow approval thresholds for restricted or high-value actions
- Security headers, rate limiting, audit event structure, encryption helpers, and data-quality profiling
- Non-root container, Kubernetes resources, probes, HPA, PDB, and NetworkPolicy

## Public Demo

- Interactive dashboard: https://arul7441.github.io/xeip/
- Principal review: https://arul7441.github.io/xeip/review.html
