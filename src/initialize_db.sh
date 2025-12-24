#!/bin/bash
# Run when INITIALIZE_DB parameter is set and migrations are available.
./manage.py migrate --check
if [ $? -ne 0 ] && "$INITIALIZE_DB" = "true";
then
    echo "--- Run migrate";
    ./manage.py migrate;
    echo "--- Import schemas";
    ./manage.py import_schemas --execute --no-migrate-tables;
    echo "--- Import scopes";
    python manage.py import_scopes;
    echo "--- Import publishers";
    python manage.py import_publishers;
    echo "--- Import profiles";
    python manage.py import_profiles;
fi
