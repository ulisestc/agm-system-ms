FROM python:3.11-slim
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY ./src ./src

# Exponemos el puerto REST y gRPC
EXPOSE 8005
EXPOSE 50055

# Comando para ejecutar FastAPI usando la ruta correcta al main
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]