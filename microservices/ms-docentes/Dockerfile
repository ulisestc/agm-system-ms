# ── Stage: MS-3 Docentes & Alumnos (FastAPI + RabbitMQ RPC) ──────────────────────────
FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=20
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Copiar e instalar dependencias de Python
COPY microservices/ms-docentes/requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary -r requirements.txt

# Copiar código fuente
COPY microservices/ms-docentes/ .

# Exponer puertos: 8003 (REST)
EXPOSE 8003

# Variables de entorno por defecto
ENV REST_PORT=8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
