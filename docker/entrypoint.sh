#!/bin/sh

echo "waiting for MySQL..."

depends_on:
    mysql:
        condition: service_healthy

echo "MySQL is ready."

python manage.py migrate --nopoint

python manage.py collectstatic --nopoint

exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    med_stream.wsgi.application