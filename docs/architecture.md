# Production Architecture

```mermaid
flowchart LR
  U["Enterprise users"] --> FE["Next.js command cockpit"]
  FE --> API["FastAPI gateway"]
  API --> AUTH["JWT, RBAC, policy checks"]
  API --> ORCH["LangGraph-style agent orchestrator"]
  ORCH --> SUP["Support Agent"]
  ORCH --> MAINT["Maintenance Agent"]
  ORCH --> INV["Inventory Agent"]
  ORCH --> CONTRACT["Contract Intelligence Agent"]
  ORCH --> CS["Customer Success Agent"]
  ORCH --> COMP["Compliance Agent"]
  ORCH --> EXEC["Executive Advisor Agent"]
  API --> RAG["RAG service"]
  RAG --> VEC["Qdrant vector index"]
  RAG --> PG["PostgreSQL operational store"]
  API --> ML["Model serving"]
  ML --> REG["Model registry"]
  API --> AUDIT["Audit log stream"]
  AUDIT --> MON["Prometheus and Grafana"]
```

## Services

- Frontend: Next.js, TypeScript, Tailwind-compatible design layer
- API gateway: FastAPI with OpenAPI docs
- Persistence: PostgreSQL for operational records, Qdrant for vectors
- ML serving: failure prediction, churn prediction, inventory forecasting, ticket classification, anomaly detection
- Agent orchestration: specialist agents coordinated through a permission-aware orchestrator
- Observability: audit stream, metrics, model confidence, workflow traces

## Production Notes

- All recommendations must include confidence, reasoning, sources, risks, and alternatives.
- RAG retrieval is permission filtered before answer generation.
- Agent actions are gated by role permissions and audited.
- Human review can be inserted for high financial, safety, or compliance risk actions.

