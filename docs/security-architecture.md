# Security Architecture

Controls implemented in the scaffold:

- JWT-shaped authentication shim for local demo
- Role-based access control with explicit permission sets
- Audit events for agent and workflow actions
- PII masking for email and phone values
- Prompt injection validation before RAG retrieval
- RAG permission filtering design
- Agent permission controls by role

Production hardening:

- Replace demo token parsing with enterprise IdP and JWKS validation
- Encrypt data at rest with KMS-managed keys
- Enforce row-level security by customer and data classification
- Add DLP scanning to document ingestion
- Require approval gates for expensive procurement and contract amendments
- Store immutable audit trails in append-only storage

