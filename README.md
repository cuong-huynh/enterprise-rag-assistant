# Enterprise RAG Assistant

An AI assistant that answers questions from internal documents (RAG) and structured ERP data (Text-to-SQL) through a single chat interface.

## Status

| Phase | Status |
|---|---|
| P0 — Skeleton (FastAPI + mock LLM) | ✅ Done |
| P1 — RAG vertical slice | ✅ Done |
| P2 — Eval harness | 🔄 In progress |
| P3 — Text-to-SQL on mock Odoo | ⬜ |
| P4 — Dispatcher | ⬜ |
| P5 — Production shell (Docker, queue, load test) | ⬜ |
| P5.5 — Deploy to VPS | ⬜ |

## Quick start

```bash
cp .env.example .env
uv sync
uv run uvicorn assistant.main:app --reload
```

Then:

```bash
# Health check
curl http://localhost:8000/health

# Ask a question (requires documents to be indexed first)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the sales order process?"}'

# Index a PDF document
curl -X POST http://localhost:8000/ingest \
  -F "file=@path/to/document.pdf"
```

## Architecture

```
src/assistant/
├── main.py                      # FastAPI factory — composition only
├── core/config.py               # Settings from .env (pydantic-settings)
├── api/routes.py                # HTTP endpoints: /health, /ask, /ingest
├── integrations/
│   ├── llm_client.py            # LLM_MODE=mock|real
│   └── vector_store.py          # Chroma singleton
└── modules/
    └── rag/
        ├── service.py           # Public gate: ask(), ingest_file()
        ├── ingest.py            # PDF loading (pypdf)
        ├── chunk.py             # RecursiveCharacterTextSplitter
        ├── index.py             # Embed + upsert to Chroma
        ├── retrieve.py          # Vector similarity search
        └── generate.py          # LLM call + citation formatting
```

Dependency rule: `api → modules → integrations → core`. Enforced by `import-linter` in CI.

## Eval (P2)

From repo root (rebuilds sample PDFs, resets Chroma, scores recall@5):

```bash
uv run python -m evals.run
```

Results are written to `evals/results/<date>.md`. Use `--skip-ingest` to reuse the current index.

## CI

GitHub Actions runs `ruff check`, `ruff format --check`, `lint-imports`, and `pytest` on every push and pull request.

## Design docs

- [RAG engine v1](docs/design/rag_v1.md)
