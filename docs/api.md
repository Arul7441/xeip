# API Documentation

FastAPI exposes OpenAPI at `/docs` when the backend is running.

Endpoints:

- `GET /health`: service health
- `GET /metrics/executive`: executive KPI payload
- `POST /agents/orchestrate`: objective-based multi-agent routing
- `POST /rag/query`: secure RAG answer with sources and confidence
- `POST /ml/failure`: printer failure probability
- `POST /ml/churn`: customer churn probability
- `POST /ml/inventory`: toner or spare-part demand forecast
- `POST /workflows/low-toner`: autonomous low-toner procurement workflow

Example:

```bash
curl -X POST http://localhost:8080/agents/orchestrate \
  -H 'content-type: application/json' \
  -d '{"objective":"low toner procurement with SLA risk","payload":{"toner_level_pct":8,"stock_on_hand":10}}'
```

