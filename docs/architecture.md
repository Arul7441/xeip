# XEIP System Architecture

## High-Level Architecture

```mermaid
flowchart TD
  U[Users and Executives] --> WEB[Next.js Dashboard / GitHub Pages Demo]
  WEB --> API[FastAPI Gateway]
  API --> ORCH[Agent Orchestrator]
  ORCH --> SUPPORT[Support Agent]
  ORCH --> MAINT[Maintenance Agent]
  ORCH --> INV[Inventory Agent]
  ORCH --> COMP[Compliance Agent]
  ORCH --> EXEC[Executive Agent]
  SUPPORT --> RAG[RAG Retrieval Layer]
  MAINT --> ML[ML Model Services]
  INV --> ML
  COMP --> AUDIT[Audit and Governance]
  EXEC --> AUDIT
  RAG --> QDRANT[Qdrant Vector Store]
  API --> PG[PostgreSQL]
  ML --> DATA[Synthetic Enterprise Datasets]
  ORCH --> LLM[LLMs / Governed Generation]
```

## Frontend Architecture

```mermaid
flowchart LR
  UI[Executive Dashboard] --> VIEWS[Command / Agents / ML / Governance / Data]
  VIEWS --> API_CLIENT[API Client]
  API_CLIENT --> FASTAPI[FastAPI Endpoints]
  VIEWS --> STATIC[Static GitHub Pages Demo]
```

The current public demo is a self-contained browser application in `docs/index.html`.
The productized app source is in `frontend/app`.

## Backend Architecture

```mermaid
flowchart TD
  REQ[HTTP Request] --> MW[Security Middleware]
  MW --> AUTH[Demo JWT/RBAC Parser]
  AUTH --> ROUTES[FastAPI Routes]
  ROUTES --> AGENTS[Agent Orchestration]
  ROUTES --> MODELS[ML Scoring]
  ROUTES --> RAG[RAG Query]
  ROUTES --> WORKFLOW[Workflow Automation]
  AGENTS --> GOV[Governance Policy]
  RAG --> OBS[Audit Events]
  WORKFLOW --> OBS
```

## Agent Architecture

```mermaid
sequenceDiagram
  participant User
  participant API as FastAPI
  participant Orchestrator
  participant Support
  participant Maintenance
  participant Inventory
  participant Executive
  User->>API: POST /chat or /agents/orchestrate
  API->>Orchestrator: Validate tenant, role, objective
  Orchestrator->>Support: Diagnose if support terms match
  Orchestrator->>Maintenance: Predict failure if downtime terms match
  Orchestrator->>Inventory: Forecast replenishment if toner terms match
  Orchestrator->>Executive: Rank decision and business impact
  Orchestrator-->>API: Recommendations + governance
  API-->>User: Governed AI response
```

## RAG Architecture

```mermaid
flowchart TD
  Q[User Query] --> GUARD[Prompt Injection Guard]
  GUARD --> ACL[RBAC Metadata Filter]
  ACL --> EMB[Embedding Model]
  EMB --> RET[Retriever]
  RET --> RERANK[Reranker]
  RERANK --> GEN[Answer Generator]
  GEN --> CITE[Source Citations]
  CITE --> AUDIT[Audit Trace]
```

The runnable RAG component layout is:

- `rag/embeddings.py`
- `rag/retriever.py`
- `rag/reranker.py`
- `rag/generator.py`
- `data/manuals`, `data/contracts`, `data/sop`, `data/tickets`

## Database Schema

The PostgreSQL schema is in `database/schema.sql` and covers tenants, devices,
telemetry, tickets, contracts, and audit events.

## API Design

Primary endpoints:

- `GET /health`
- `GET /metrics/executive`
- `POST /chat`
- `POST /agents/orchestrate`
- `POST /rag/query`
- `POST /predict-failure`
- `POST /predict-churn`
- `POST /forecast-toner`
- `POST /route-ticket`
- `POST /detect-anomaly`
- `POST /create-workorder`
- `POST /analyze-contract`
- `POST /workflows/low-toner`
- `GET /data-quality`

