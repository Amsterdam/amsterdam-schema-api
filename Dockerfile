FROM ghcr.io/astral-sh/uv:0.11-python3.14-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    libgeos-dev \
    libpq-dev \
    curl

WORKDIR /app
COPY . ./

RUN uv sync --frozen --no-install-project --all-groups

FROM ghcr.io/astral-sh/uv:0.11-python3.14-trixie-slim

RUN groupadd --system --gid 999  schemaapi  && useradd --system --gid 999 \
    --uid 1001 --create-home schemaapi
RUN apt update && apt install --no-install-recommends -y \
    build-essential \
    curl \
    gdal-bin \
    libgdal-dev \
    git

WORKDIR /app

RUN chown schemaapi:schemaapi /app
COPY --from=builder --chown=schemaapi:schemaapi /app /app
USER schemaapi

ENV DJANGO_SETTINGS_MODULE=schema_api.settings \
    DJANGO_DEBUG=false \
    UWSGI_HTTP_SOCKET=:8000 \
    UWSGI_MODULE=schema_api.wsgi \
    UWSGI_CALLABLE=application \
    UWSGI_MASTER=1

RUN uv run src/manage.py collectstatic --noinput
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT []
EXPOSE 8000

CMD ["uv", "run","uwsgi"]
