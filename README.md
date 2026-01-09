# Amsterdam Schema API

A Django REST API to expose the [Amsterdam Schema](https://github.com/Amsterdam/amsterdam-schema).

## Installation

Requirements:

* Python >= 3.12
* Recommended: Docker/Docker Compose (or pyenv for local installs)

### Using Docker Compose

Run docker compose:
```shell
docker compose up
```

Navigate to `localhost:8000`.

### Using Local Python

Create a virtualenv:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

Install all packages in it:
```shell
pip install -U wheel pip
pip install setuptools
cd src/
make install  # installs src/requirements_dev.txt
```

Execute the following commands to migrate and fill the database:

```shell
python manage.py migrate
python manage.py import_schemas --execute --no-migrate-tables
python manage.py import_scopes
python manage.py import_publishers
python manage.py import_profiles
```

Set the required environment variables and start the Django application:
```shell
export PUB_JWKS="$(cat jwks_test.json)"
export DJANGO_DEBUG=true

./manage.py runserver localhost:8000
```

## Available endpoints

The following URLs are available:

| API                                      | Description                              |
|------------------------------------------|------------------------------------------|
| `/datasets/` | All available datasets (without inlined tables)                          |
| `/datasets/<dataset_id>/` | Dataset with inlined tables             |
| `/datasets/<dataset_id>/?scopes=[scope_list]/` | Dataset with inlined tables, filtered on scope       |
| `/datasets/<dataset_id>/<vmajor>/` | Specific major version of dataset with inlined tables     |
| `/datasets/<dataset_id>/<vmajor>/?scopes=[scope_list]/` | Specific major version of dataset with inlined tables, filtered on scope  |
| `/datasets/<dataset_id>/<vmajor><table_id>/` | Table of specific major version of dataset |
| `/datasets/<dataset_id>/<vmajor><table_id>/?scopes=[scope_list]/`| Table of specific major version of dataset, filtered on scope |
| `/scopes/` | All available scopes |
| `/scopes/<scope_id>/` | Scope details |
| `/publishers/` |  All available publishers |
| `/publishers/<publisher_id>/` | Publisher details |
| `/profiles/` | All available profiles |
| `/profiles/<profiles_id>/` | Profile details |
| `/changelog/` | All changelog items |
| `/changelog/?from_date='YYYY-MM-DD'/` | Changelog items newer than provided from_date |
| `/changelog/<dataset_id>/` | Changelog items for a specific dataset |
| `/changelog/<dataset_id>?from_date='YYYY-MM-DD'/` | Changelog items for a specific dataset, newer than provided from_date |
| `/changelog/<changelog_id>/` | Changelog item details |

## Environment Settings

The following environment variables are useful for configuring a local development environment:

* `DJANGO_DEBUG` to enable debugging (true/false).
* `LOG_LEVEL` log level for application code (default is `DEBUG` for debug, `INFO` otherwise).
* `AUDIT_LOG_LEVEL` log level for audit messages (default is `INFO`).
* `DJANGO_LOG_LEVEL` log level for Django internals (default is `INFO`).
* `PUB_JWKS` allows to give publically readable JSON Web Key Sets in JSON format (good default: `jq -c < src/jwks_test.json`).

Deployment:

* `ALLOWED_HOSTS` will limit which domain names can connect.
* `AZURE_APPI_CONNECTION_STRING` Azure Insights configuration.
* `AZURE_APPI_AUDIT_CONNECTION_STRING` Same, for a special audit logging.
* `CLOUD_ENV=azure` will enable Azure-specific telemetry.
* `OAUTH_JWKS_URL` point to a public JSON Web Key Set, e.g. `https://login.microsoftonline.com/{tenant_uuid or 'common'}/discovery/v2.0/keys`.
* `OAUTH_CHECK_CLAIMS` should be `aud=AUDIENCE-IN-TOKEN,iss=ISSUER-IN-TOKEN`.

Hardening deployment:

* `SESSION_COOKIE_SECURE` is already true in production.
* `CSRF_COOKIE_SECURE` is already true in production.
* `SECRET_KEY` is used for various encryption code.
* `CORS_ALLOW_ALL_ORIGINS` can be true/false to allow all websites to connect.
* `CORS_ALLOWED_ORIGINS` allows a list of origin URLs to use.
* `CORS_ALLOWED_ORIGIN_REGEXES` supports a list of regex patterns fow allowed origins.

## Developer Notes

Run `make` in the `src` folder to have a help-overview of all common developer tasks.

## Package Management

The packages are managed with *pip-compile*.

To add a package, update the `requirements.in` file and run `make requirements`.
This will update the "lockfile" aka `requirements.txt` that's used for pip installs.

To upgrade all packages, run `make upgrade`, followed by `make install` and `make test`.
Or at once if you feel lucky: `make upgrade install test`.

## Environment Settings

Consider using *direnv* for automatic activation of environment variables.
It automatically sources an ``.envrc`` file when you enter the directory.
This file should contain all lines in the `export VAR=value` format.

In a similar way, *pyenv* helps to install the exact Python version,
and will automatically activate the virtualenv when a `.python-version` file is found:

```shell
pyenv install 3.12.4
pyenv virtualenv 3.12.4 dataselectie-proxy
echo dataselectie-proxy > .python-version
```

## Changelog Management command

The Changelog management command clones the Amsterdam Schema repository, goes through all new commits and extracts changes for each database.
These changes are exported to a changelog table, and can be accessed with the `/changelog/` endpoint.

### Usage

```
./manage.py changelog (--start_commit [start_commit]) (--end_commit [end_commit])
```

The command can be run with or without the following optional arguments:

* `start_commit`: if a start commit is provided as a command line argument, the changelog will be generated starting from this commit.
Commits made before this point in time will not be taken into account. If the start commit is not provided as a command line argument,
the commit from the most recent changelog record will be used as the start commit. This is the default behaviour. If there are no records in the changelog table,
a fixed commit (`418e137ff39c1d0ef9e224067627fe300ff9f4a1`)  will be the start commit.
* `end_commit`: if an end commit is provided as a commind line argument, the changelog will be generated from the start commit to this commit.
Commits made after this point of time will not be taken into account. If the end commit is not provided as a command line argument,
the changelog be generated up to the current master branch. This is the default behaviour.

Specifying a range of commits (by supplying a start and end commit) can be handy when there has been a change in the logic of the changelog command and you need to check if the change finds any previously missed changelog updates.
