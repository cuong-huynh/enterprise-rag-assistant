"""Fetch PDF attachments from Odoo for RAG indexing."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from assistant.integrations.odoo_rpc import OdooRpcClient

# Universal store: every Odoo app (Documents, Knowledge, SO, Project…) saves files here.
ATTACHMENT_MODEL = "ir.attachment"

PDF_MIMETYPES = frozenset({"application/pdf", "application/x-pdf"})


@dataclass(frozen=True)
class OdooPdfAttachment:
    """A PDF binary stored on ``ir.attachment``."""

    attachment_id: int
    name: str
    res_model: str
    res_id: int
    mimetype: str
    write_date: str
    content: bytes

    @property
    def citation_name(self) -> str:
        """Stable display name / Chroma ``source`` for re-sync."""
        safe = re.sub(r"[^\w.\-]+", "_", self.name).strip("_") or "document.pdf"
        prefix = self.res_model.replace(".", "-") if self.res_model else "attachment"
        return f"odoo-{prefix}-{self.attachment_id}-{safe}"


def _parse_write_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def list_pdf_attachments(
    client: OdooRpcClient,
    *,
    since: datetime | None = None,
    limit: int = 50,
    res_models: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return attachment metadata (without ``datas``) from Odoo."""
    domain: list[Any] = [
        ("type", "=", "binary"),
        ("mimetype", "in", list(PDF_MIMETYPES)),
    ]
    if since is not None:
        domain.append(("write_date", ">", since.strftime("%Y-%m-%d %H:%M:%S")))
    if res_models:
        domain.append(("res_model", "in", res_models))

    return client.search_read(
        ATTACHMENT_MODEL,
        domain,
        fields=["id", "name", "mimetype", "res_model", "res_id", "write_date"],
        limit=limit,
        order="write_date asc",
    )


def download_pdf_attachment(client: OdooRpcClient, attachment_id: int) -> OdooPdfAttachment:
    """Load one attachment including base64 ``datas``."""
    rows = client.search_read(
        ATTACHMENT_MODEL,
        [("id", "=", attachment_id)],
        fields=["id", "name", "mimetype", "res_model", "res_id", "write_date", "datas"],
        limit=1,
    )
    if not rows:
        raise ValueError(f"Odoo attachment {attachment_id} not found")

    row = rows[0]
    raw = row.get("datas")
    if not raw:
        raise ValueError(f"Odoo attachment {attachment_id} has no datas payload")

    content = base64.b64decode(raw, validate=False)
    mimetype = str(row.get("mimetype") or "application/pdf")
    if mimetype not in PDF_MIMETYPES:
        raise ValueError(f"Attachment {attachment_id} is not PDF ({mimetype})")

    return OdooPdfAttachment(
        attachment_id=int(row["id"]),
        name=str(row.get("name") or f"attachment-{attachment_id}.pdf"),
        res_model=str(row.get("res_model") or ""),
        res_id=int(row.get("res_id") or 0),
        mimetype=mimetype,
        write_date=str(row.get("write_date") or ""),
        content=content,
    )


def filter_by_since(rows: list[dict[str, Any]], since: datetime | None) -> list[dict[str, Any]]:
    if since is None:
        return rows
    kept: list[dict[str, Any]] = []
    for row in rows:
        parsed = _parse_write_date(str(row.get("write_date") or ""))
        if parsed is None or parsed > since:
            kept.append(row)
    return kept
