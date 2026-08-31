"""One-time local setup: mock ERP DB + sample PDFs in Chroma (if empty).

Usage (from repo root)::

    uv sync
    uv run python scripts/bootstrap_local.py
    # edit .env → OPENAI_API_KEY=sk-...
    uv run uvicorn assistant.main:app --reload
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from generate_mock_odoo import generate as generate_mock_odoo  # noqa: E402
from generate_sample_docs import generate_all  # noqa: E402

from assistant.integrations.vector_store import get_collection  # noqa: E402
from assistant.modules.rag import service as rag_service  # noqa: E402

DB_PATH = ROOT / "data" / "mock_odoo.sqlite"


async def _ensure_rag_index() -> int:
    count = get_collection().count()
    if count > 0:
        print(f"Chroma already has {count} chunks — skip ingest.")
        return count

    pdfs = generate_all()
    total = 0
    for path in pdfs:
        result = await rag_service.ingest_file(path, display_name=path.name)
        total += result.num_chunks
        print(f"Ingested {result.file}: {result.num_chunks} chunks")
    return total


def _ensure_mock_erp() -> Path:
    if DB_PATH.exists():
        print(f"Mock Odoo DB exists: {DB_PATH}")
        return DB_PATH
    generate_mock_odoo()
    print(f"Created mock Odoo DB: {DB_PATH}")
    return DB_PATH


async def main() -> None:
    _ensure_mock_erp()
    chunks = await _ensure_rag_index()
    print(f"Bootstrap done. Chroma chunks indexed this run: {chunks if chunks else 'reused'}")
    print("Next: set OPENAI_API_KEY in .env, then uv run uvicorn assistant.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
