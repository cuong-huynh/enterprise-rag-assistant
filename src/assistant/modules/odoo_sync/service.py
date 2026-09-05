"""Public gate: pull Odoo PDF attachments into Chroma via ``rag.service``."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from assistant.core.config import settings
from assistant.integrations.odoo_rpc import OdooRpcClient
from assistant.modules.odoo_sync.fetch import (
    download_pdf_attachment,
    filter_by_since,
    list_pdf_attachments,
)
from assistant.modules.rag import service as rag_service


@dataclass
class OdooSyncResult:
    scanned: int = 0
    indexed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)


def _staging_dir() -> Path:
    path = settings.ingest_inbox_dir.parent / "odoo"
    path.mkdir(parents=True, exist_ok=True)
    return path


async def sync_pdf_attachments(
    *,
    since: datetime | None = None,
    limit: int = 50,
    res_models: list[str] | None = None,
    client: OdooRpcClient | None = None,
) -> OdooSyncResult:
    """Cron/pull entry: fetch PDF ``ir.attachment`` rows and index into Chroma.

    ``res_models`` optionally limits to apps, e.g. ``documents.document``,
    ``knowledge.article``, ``sale.order``. Default: all models (via ir.attachment).
    """
    result = OdooSyncResult()
    rpc = client or OdooRpcClient()
    staging = _staging_dir()

    try:
        rows = list_pdf_attachments(rpc, since=since, limit=limit, res_models=res_models)
    except Exception as exc:  # noqa: BLE001 — surface as sync summary
        result.errors.append(f"list attachments: {exc}")
        return result

    rows = filter_by_since(rows, since)
    result.scanned = len(rows)

    for row in rows:
        att_id = int(row["id"])
        tmp_path = staging / f"sync_{uuid.uuid4().hex}_{att_id}.pdf"
        try:
            attachment = download_pdf_attachment(rpc, att_id)
            tmp_path.write_bytes(attachment.content)
            ingest = await rag_service.ingest_file(
                tmp_path,
                display_name=attachment.citation_name,
            )
            result.indexed += 1
            result.files.append(ingest.file)
        except Exception as exc:  # noqa: BLE001 — continue other attachments
            result.skipped += 1
            result.errors.append(f"attachment {att_id}: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)

    return result
