# ── Stage: MS-3 Docentes & Alumnos (FastAPI + RabbitMQ RPC) ──────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para pdfplumber y psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY microservices/ms-docentes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY microservices/ms-docentes/ .

# Exponer puertos: 8003 (REST)
EXPOSE 8003

# Variables de entorno por defecto
ENV REST_PORT=8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
