FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y reportlab
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias primero
COPY microservices/ms-reportes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/ms-reportes/ .
COPY proto/reportes.proto /proto/reportes.proto

RUN python -m grpc_tools.protoc \
    -I/proto \
    --python_out=. \
    --grpc_python_out=. \
    /proto/reportes.proto

# Puerto REST (FastAPI/uvicorn)
EXPOSE 8007
# Puerto gRPC (interno entre microservicios)
EXPOSE 50057

# Iniciar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
