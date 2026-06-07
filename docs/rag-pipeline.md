# RAG Pipeline

```mermaid
flowchart TD
  A["Knowledge sources"] --> B["Document loader"]
  B --> C["Chunking and metadata extraction"]
  C --> D["PII detection and security labeling"]
  D --> E["Embedding generation"]
  E --> F["Qdrant vector storage"]
  C --> G["PostgreSQL document catalog"]
  Q["User query"] --> H["Prompt injection validation"]
  H --> I["Hybrid search"]
  I --> J["RBAC metadata filter"]
  J --> K["Reranking"]
  K --> L["Context compression"]
  L --> M["Response generation"]
  M --> N["Citation, confidence, risk, alternatives"]
```

Knowledge sources include product manuals, SOPs, maintenance guides, historical support tickets, contracts, compliance policies, security procedures, product specifications, training documents, and service engineering notes.

