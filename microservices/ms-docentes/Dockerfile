# ── Stage: MS-3 Docentes & Alumnos (FastAPI + gRPC) ──────────────────────────
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

# Generar código gRPC desde el proto
COPY proto/alumnosdocentes.proto /proto/alumnosdocentes.proto
RUN python -m grpc_tools.protoc \
    --proto_path=/proto \
    --python_out=src/grpc_generated \
    --grpc_python_out=src/grpc_generated \
    /proto/alumnosdocentes.proto && \
    sed -i 's/import alumnosdocentes_pb2 as alumnosdocentes__pb2/from src.grpc_generated import alumnosdocentes_pb2 as alumnosdocentes__pb2/' src/grpc_generated/alumnosdocentes_pb2_grpc.py

# Exponer puertos: 8003 (REST) y 50053 (gRPC)
EXPOSE 8003 50053

# Variables de entorno por defecto (serán sobreescritas por docker-compose)
ENV REST_PORT=8003
ENV GRPC_PORT=50053

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
