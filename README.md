# Enterprise RAG Assistant

An AI assistant that answers questions from internal documents (RAG) and structured ERP data (Text-to-SQL) through a single chat interface.

## Status

| Phase | Status |
|---|---|
| P0 — Skeleton (FastAPI + mock LLM) | Done |
| P1 — RAG vertical slice | Done |
| P2 — Eval harness | Done |
| P2+ — RAG v2 (API embed + LangGraph agent) | Done |
| P3 — Text-to-SQL on mock Odoo | Done |
| P4 — Dispatcher | Done |
| P5 — Production shell (Docker, queue, load test) | In progress |
| P5.5 — Deploy to VPS | Pending |

## Quick start

```bash
cp .env.example .env
uv sync
uv run python scripts/bootstrap_local.py --reset-chroma   # first run or after embed model change
uv run uvicorn assistant.main:app --reload --host 0.0.0.0
```

### CLI (RAG only)

```bash
# Ingest a PDF (wipe Chroma first if switching embed model)
uv run rag-cli ingest --file path/to/document.pdf --reset

# Ask against indexed docs
uv run rag-cli ask "What are the warehouse outbound steps?"
```

### HTTP

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

# Unified chat (dispatcher: rag / data / hybrid)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many confirmed sale orders?"}'
```

## Environment

| Variable | Purpose |
|---|---|
| `LLM_MODE` | `mock` (CI) or `real` (OpenAI-compatible chat) |
| `EMBED_MODE` | `mock` (deterministic hash vectors) or `api` (Gemini/OpenAI embed) |
| `EMBED_MODEL` | e.g. `text-embedding-004` when using Google OpenAI-compatible endpoint |
| `ERP_MODE` | `mock` (SQLite) or `odoo` (XML-RPC live) |

**Important:** changing `EMBED_MODE` or `EMBED_MODEL` changes the vector space. Wipe and rebuild Chroma:

```bash
uv run python scripts/bootstrap_local.py --reset-chroma
# or
uv run rag-cli ingest --file your.pdf --reset
```

## Architecture

```
src/assistant/
├── cli.py                       # rag-cli: ingest | ask
├── main.py                      # FastAPI factory
├── core/config.py               # Settings from .env
├── integrations/
│   ├── embedding_client.py      # EMBED_MODE=mock|api
│   ├── llm_client.py            # LLM_MODE=mock|real
│   └── vector_store.py          # Chroma singleton + delete-by-source
└── modules/
    └── rag/
        ├── service.py           # Public gate: ask(), ingest_file()
        ├── config.py
        ├── ingestion/           # load PDF, chunk
        ├── indexing/            # embed → Chroma
        ├── retrieval/           # vector search, expand_query
        ├── generation/          # LLM + citations
        └── orchestration/       # LangGraph ask flow
```

Dependency rule: `api → modules → integrations → core`. Enforced by `import-linter` in CI.

## Eval (P2)

From repo root (rebuilds sample PDFs, resets Chroma, scores recall@5):

```bash
# CI / offline (mock embed + mock LLM)
$env:LLM_MODE='mock'; $env:EMBED_MODE='mock'
uv run python -m evals.run
```

Results are written to `evals/results/<date>.md`. Use `--skip-ingest` to reuse the current index.

## CI

GitHub Actions runs `ruff check`, `ruff format --check`, `lint-imports`, and `pytest` on every push and pull request.

## Design docs

- [RAG engine v1](docs/design/rag_v1.md) — frozen P1/P2 design (MiniLM, linear)
- [RAG engine v2](docs/design/rag_v2.md) — current (API embed, LangGraph)
