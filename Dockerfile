# aptagent — runs the weekly pipeline (`aptagent run`) on Railway's cron.
FROM python:3.12-slim

# uv for fast, reproducible installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install deps first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# App code + config
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini preferences.yaml ./
RUN uv sync --frozen --no-dev

# Apply migrations, then run the weekly pipeline once and exit (cron re-invokes).
CMD ["sh", "-c", "uv run alembic upgrade head && uv run aptagent run"]
