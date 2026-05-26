#!/bin/sh
set -eu

until python -c "import os, psycopg2; psycopg2.connect(host=os.getenv('DB_HOST','db'), port=os.getenv('DB_PORT','5432'), dbname=os.getenv('DB_NAME','agm_periodos_materias_db'), user=os.getenv('DB_USER','postgres'), password=os.getenv('DB_PASSWORD','postgres')); print('db ready')"; do
  sleep 2
done

python manage.py migrate --run-syncdb
python manage.py runrabbitmq &
exec python manage.py runserver 0.0.0.0:8000
