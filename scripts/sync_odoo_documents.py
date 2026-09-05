"""Pull PDF attachments from Odoo and index into Chroma (cron-friendly).

Usage (Odoo live, from repo root)::

    # .env: ERP_MODE=odoo, ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
    uv run python scripts/sync_odoo_documents.py
    uv run python scripts/sync_odoo_documents.py --limit 20
    uv run python scripts/sync_odoo_documents.py --model documents.document
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from assistant.core.config import settings  # noqa: E402
from assistant.modules.odoo_sync.service import sync_pdf_attachments  # noqa: E402


async def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Odoo PDF attachments into RAG index")
    parser.add_argument("--limit", type=int, default=50, help="Max attachments per run")
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Filter ir.attachment by res_model (repeatable). Example: knowledge.article",
    )
    args = parser.parse_args()

    if settings.erp_mode != "odoo":
        print("Set ERP_MODE=odoo in .env to sync from a live Odoo instance.", file=sys.stderr)
        return 1

    print(f"Odoo sync → {settings.odoo_url} (db={settings.odoo_db})")
    result = await sync_pdf_attachments(limit=args.limit, res_models=args.models)

    print(f"Scanned: {result.scanned}  |  Indexed: {result.indexed}  |  Skipped: {result.skipped}")
    for name in result.files:
        print(f"  + {name}")
    for err in result.errors:
        print(f"  ! {err}", file=sys.stderr)

    return 0 if result.indexed > 0 or (result.scanned == 0 and not result.errors) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
