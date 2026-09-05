# Docker (P5)

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- Copy `.env.example` → `.env` at repo root (API key optional when `LLM_MODE=mock`)

## First-time data

Compose shares a `app-data` volume for Chroma + mock Odoo. Seed once:

```bash
# from repo root, with stack running or volume mounted
uv run python scripts/bootstrap_local.py
```

Or run bootstrap inside the API container after `docker compose up`.

## Start stack

From **repository root**:

```bash
docker compose -f infra/docker-compose.yml up --build
```

- Chat UI: http://localhost:8000/
- `POST /ingest` returns `status=queued` — worker embeds in background
- `POST /chat` stays responsive during large PDF ingest

## Load test (optional)

```bash
k6 run infra/k6/chat.js
```

Uses `LLM_MODE=mock` against `http://localhost:8000/chat`.
