# XEIP Enterprise Intelligence API — production container
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first for better layer caching
COPY backend/requirements-prod.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Application code + datasets (analytics reads /app/data at runtime)
COPY backend/ ./backend/
COPY data/ ./data/

WORKDIR /app/backend
EXPOSE 8081

# Render (and most PaaS) inject $PORT; default to 8081 for local runs
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8081}"]
