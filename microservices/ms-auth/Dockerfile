# Base image ligera con Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema necesarias para psycopg2 y compilación de paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY microservices/ms-auth/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del microservicio
COPY microservices/ms-auth/ .
COPY proto/auth.proto .
COPY proto/notificaciones.proto .

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. auth.proto
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notificaciones.proto

# Puerto REST y, si se usa, puerto gRPC
EXPOSE 8000 50051

# Variables de entorno por defecto (docker-compose puede sobreescribirlas)
ENV PYTHONUNBUFFERED=1
ENV REST_PORT=8000
ENV GRPC_PORT=50051

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
