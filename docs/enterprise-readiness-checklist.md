# Enterprise Readiness Checklist

| Control | Status | Notes |
| --- | --- | --- |
| Auth required | Implemented | Demo parser still needs enterprise IdP replacement |
| RBAC | Implemented | Permission checks added to API, RAG, agents, workflow |
| Tenant isolation | Implemented | Tenant scope enforced from governance envelope |
| Audit trail | Implemented for demo | Production must use append-only external store |
| Prompt injection guard | Implemented | Rule-based demo, should be replaced with layered classifier and allowlist |
| RAG abstention | Implemented | No evidence means no answer |
| Model cards | Implemented | Baseline metadata added to scoring output |
| Model input validation | Implemented | Pydantic bounds added |
| Data quality gate | Implemented | `/data-quality` endpoint profiles CSVs |
| Workflow approvals | Implemented | High impact/restricted/high risk requires human approval |
| Container hardening | Implemented | Non-root user, pinned image, no bytecode |
| Kubernetes hardening | Implemented | HPA, PDB, resources, probes, network policy |
| SLOs | Documented | Needs live Prometheus rules |
| Disaster recovery | Gap | Add backup/restore and regional failover plans |
| Vendor risk | Gap | Add model/provider SLA, fallback, and data-processing agreements |

