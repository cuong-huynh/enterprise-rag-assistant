# Build context: repository root (parent of infra/).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src ./src
COPY configs ./configs
COPY scripts ./scripts

EXPOSE 8000

# Default: API. Worker service overrides command in docker-compose.
CMD ["uv", "run", "--no-dev", "uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "8000"]
