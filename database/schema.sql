CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
  device_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  printer_id TEXT NOT NULL,
  device_type TEXT NOT NULL,
  customer TEXT NOT NULL,
  region TEXT NOT NULL,
  installed_at DATE
);

CREATE TABLE IF NOT EXISTS printer_telemetry (
  event_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  device_id TEXT NOT NULL REFERENCES devices(device_id),
  observed_at TIMESTAMPTZ NOT NULL,
  temperature NUMERIC(6,2) NOT NULL,
  usage_hours NUMERIC(10,2) NOT NULL,
  error_count INTEGER NOT NULL,
  toner_level NUMERIC(5,2) NOT NULL,
  last_maintenance DATE,
  anomaly_flag BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS service_tickets (
  ticket_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  device_id TEXT REFERENCES devices(device_id),
  priority TEXT NOT NULL,
  category TEXT NOT NULL,
  sentiment NUMERIC(4,3),
  sla_met BOOLEAN,
  summary TEXT,
  opened_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS contracts (
  contract_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
  customer TEXT NOT NULL,
  sla_uptime_pct NUMERIC(5,2) NOT NULL,
  response_time_hours NUMERIC(6,2) NOT NULL,
  monthly_value_usd NUMERIC(12,2) NOT NULL,
  renewal_risk NUMERIC(5,4) NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
  audit_id BIGSERIAL PRIMARY KEY,
  request_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  resource TEXT NOT NULL,
  decision TEXT NOT NULL,
  risk_score NUMERIC(5,4) NOT NULL,
  evidence JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_tenant_device_time ON printer_telemetry(tenant_id, device_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_tenant_priority ON service_tickets(tenant_id, priority);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_request ON audit_events(tenant_id, request_id);

INSERT INTO tenants (tenant_id, name)
VALUES ('demo-tenant', 'Demo Xerox Enterprise Tenant')
ON CONFLICT (tenant_id) DO NOTHING;

