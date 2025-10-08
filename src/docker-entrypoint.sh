#!/bin/sh

# These commands are run when the container is started
python manage.py migrate
python manage.py import_schemas --execute --no-migrate-tables
python manage.py import_scopes
python manage.py import_publishers
python manage.py import_profiles
uwsgi --py-auto-reload=1 --enable-threads --lazy-apps --buffer-size=65535
