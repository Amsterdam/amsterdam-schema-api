FROM python:3.12-slim-bullseye AS builder
MAINTAINER datapunt@amsterdam.nl

RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    libgeos-dev \
    libpq-dev \
    curl

COPY requirements* ./
ARG PIP_REQUIREMENTS=requirements.txt
RUN python -m pip install uwsgi
# The `--no-deps` has been added because of a pip bug with --require-hashes
# The dependencies have already been resolved during the generation of
# the requirements.txt, so adding `--no-deps` can safely be done.
RUN python -m pip install --no-cache-dir --no-deps -r $PIP_REQUIREMENTS

# Start runtime image,
FROM python:3.12-slim-bullseye
RUN useradd -U -r schemaapi
RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    curl \
    libgdal28 \
    netcat-openbsd

# Copy python build artifacts from builder image
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Update sqlite3
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}
RUN mkdir -p /tmp/build/sqlite && \
    curl -L https://www.sqlite.org/2024/sqlite-autoconf-3470000.tar.gz | \
        tar xz -C /tmp/build/sqlite --strip-components=1 && \
    cd /tmp/build/sqlite && \
    CFLAGS="-DSQLITE_ENABLE_COLUMN_METADATA=1" ./configure && \
    make && \
    make install && \
    python -c "import sqlite3; assert sqlite3.sqlite_version == '3.47.0'" && \
    cd / && rm -rf /tmp/build

WORKDIR /app
COPY . ./

# Have some defaults so the container is easier to start
ENV DJANGO_SETTINGS_MODULE=schema_api.settings \
    DJANGO_DEBUG=false \
    UWSGI_HTTP_SOCKET=:8000 \
    UWSGI_MODULE=schema_api.wsgi \
    UWSGI_CALLABLE=application \
    UWSGI_MASTER=1
RUN pip install setuptools  # workaround for missing pkg_resources in opentelemetry
RUN python manage.py collectstatic --noinput

# Give user permission to modify sqlite db
RUN chown schemaapi /app

EXPOSE 8000
USER schemaapi
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
