FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "until python -c \"import os, psycopg2; psycopg2.connect(host=os.getenv('DB_HOST','materias-db'), port=os.getenv('DB_PORT','5432'), dbname=os.getenv('DB_NAME','agm_materias_db'), user=os.getenv('DB_USER','postgres'), password=os.getenv('DB_PASSWORD','postgres')); print('db ready')\"; do sleep 2; done && python manage.py migrate --run-syncdb && python manage.py runserver 0.0.0.0:8000"]
