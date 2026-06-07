# Deployment Guide

## Local API

```powershell
cd C:\Users\KAIPULLA\Desktop\xeip\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8080
```

## Docker Compose

```powershell
cd C:\Users\KAIPULLA\Desktop\xeip
docker compose up --build
```

This starts:

- XEIP FastAPI API on `http://localhost:8080`
- PostgreSQL on `localhost:5432`
- Qdrant on `localhost:6333`

## Kubernetes

```powershell
kubectl apply -f deploy/kubernetes.yaml
```

## Helm

```powershell
helm install xeip helm/xeip --namespace xeip --create-namespace
```

## Terraform

```powershell
cd terraform
terraform init
terraform apply
```

