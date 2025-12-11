#!/bin/bash
set -e

echo "--- Run migrate"
python manage.py migrate

echo "--- Import_schemas"
python manage.py import_schemas --execute --no-migrate-tables

echo "--- Import scopes"
python manage.py import_scopes

echo "--- Import publishers"
python manage.py import_publishers

echo "--- Import profiles"
python manage.py import_profiles

echo "--- Start uWSGI..."
exec uwsgi \
    --py-auto-reload=1 \
    --enable-threads \
    --lazy-apps \
    --buffer-size=65535 \
    --single-interpreter \
    --need-app \
    --memory-report
