# Base image ligera con Python 3.11
FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=20
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Copiar e instalar dependencias de Python
COPY microservices/ms-auth/requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary -r requirements.txt

# Copiar el código fuente del microservicio
COPY . .

# Puerto REST
EXPOSE 8000

# Variables de entorno por defecto (docker-compose puede sobreescribirlas)
ENV PYTHONUNBUFFERED=1
ENV REST_PORT=8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
