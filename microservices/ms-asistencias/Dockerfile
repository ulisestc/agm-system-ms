FROM python:3.11-slim
WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=20
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

COPY microservices/ms-asistencias/requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary -r requirements.txt

COPY microservices/ms-asistencias/src ./src

EXPOSE 8005

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
