#!/bin/bash
# Run when INITIALIZE_DB parameter is set and migrations are available.
uv run src/manage.py migrate --check
if [ $? -ne 0 ] && "$INITIALIZE_DB" = "true";
then
    echo "--- Run migrate";
    uv run src/manage.py migrate;
    echo "--- Import schemas";
    uv run src/manage.py import_schemas --no-migrate-tables;
    echo "--- Import scopes";
    uv run src/manage.py import_scopes;
    echo "--- Import publishers";
    uv run src/manage.py import_publishers;
    echo "--- Import profiles";
    uv run src/manage.py import_profiles;
fi
