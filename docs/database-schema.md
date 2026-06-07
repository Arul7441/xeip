# Database Schema

`database/schema.sql` creates:

- `tenants`
- `devices`
- `printer_telemetry`
- `service_tickets`
- `contracts`
- `audit_events`

The schema is loaded automatically by `docker-compose.yml` when PostgreSQL starts.

```mermaid
erDiagram
  tenants ||--o{ devices : owns
  tenants ||--o{ printer_telemetry : scopes
  tenants ||--o{ service_tickets : scopes
  tenants ||--o{ contracts : scopes
  tenants ||--o{ audit_events : scopes
  devices ||--o{ printer_telemetry : emits
  devices ||--o{ service_tickets : receives
```

