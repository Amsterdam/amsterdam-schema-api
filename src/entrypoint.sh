#!/bin/sh

# These commands are run when the container is started
python manage.py migrate
echo "Importing schemas..."
python manage.py import_schemas --execute --no-migrate-tables
python manage.py import_scopes
python manage.py import_publishers
python manage.py import_profiles
uwsgi
