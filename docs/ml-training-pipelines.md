# ML Training Pipelines

```mermaid
flowchart LR
  RAW["Synthetic and enterprise raw data"] --> QC["Quality checks"]
  QC --> FEAT["Feature engineering"]
  FEAT --> SPLIT["Temporal train/validation/test split"]
  SPLIT --> TRAIN["Model training"]
  TRAIN --> EVAL["Evaluation and bias checks"]
  EVAL --> REG["Model registry"]
  REG --> SERVE["FastAPI model serving"]
  SERVE --> MON["Drift and performance monitoring"]
```

Models:

- Printer failure prediction: logistic baseline, XGBoost production candidate
- Customer churn prediction: gradient boosted classifier
- Inventory forecasting: rolling baseline, Prophet/XGBoost candidate
- Ticket classification: TF-IDF baseline, transformer candidate
- Anomaly detection: isolation forest and rules hybrid

Metrics:

- Failure and churn: ROC-AUC, PR-AUC, calibration
- Inventory: MAPE, WAPE, stockout reduction
- Ticket classification: macro F1, escalation precision
- Anomaly: alert precision, time to detect

