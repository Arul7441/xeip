# Deployment Guide

Local:

```bash
python3 scripts/generate_enterprise_data.py
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Container:

```bash
docker build -f deploy/Dockerfile.api -t xeip-api .
docker run -p 8080:8080 xeip-api
```

Kubernetes:

```bash
kubectl apply -f deploy/kubernetes.yaml
```

Production dependencies:

- PostgreSQL 16+
- Qdrant 1.12+
- Prometheus and Grafana
- Enterprise IdP for JWT validation
- Object storage for document sources and audit evidence

