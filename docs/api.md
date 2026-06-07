# XEIP API Design

All protected endpoints use the demo authorization format:

```text
Authorization: Bearer demo.demo-tenant.executive
```

Valid roles: `executive`, `operations`, `support`, `auditor`.

## Example Agent Request

```http
POST /chat
Content-Type: application/json
Authorization: Bearer demo.demo-tenant.executive
```

```json
{
  "objective": "low toner procurement for fleet",
  "payload": {
    "daily_usage": [12, 14, 13],
    "stock_on_hand": 10
  },
  "governance": {
    "request_id": "req-00001",
    "tenant_id": "demo-tenant",
    "business_impact_usd": 2000
  }
}
```

## Model Endpoints

- `POST /predict-failure`
- `POST /predict-churn`
- `POST /forecast-toner`
- `POST /route-ticket`
- `POST /detect-anomaly`

Each response includes confidence, model card metadata, drift score, drivers,
and a recommended action.

