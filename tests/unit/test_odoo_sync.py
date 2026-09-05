"""Unit tests for Odoo document sync (no live Odoo required)."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest

from assistant.modules.odoo_sync.fetch import (
    download_pdf_attachment,
    list_pdf_attachments,
)
from assistant.modules.odoo_sync.service import sync_pdf_attachments


@pytest.fixture
def rpc() -> MagicMock:
    return MagicMock()


def test_list_pdf_attachments_builds_domain(rpc: MagicMock) -> None:
    rpc.search_read.return_value = [{"id": 1, "name": "sop.pdf"}]

    rows = list_pdf_attachments(rpc, limit=10, res_models=["documents.document"])

    rpc.search_read.assert_called_once()
    model, domain = rpc.search_read.call_args[0][:2]
    assert model == "ir.attachment"
    assert ("res_model", "in", ["documents.document"]) in domain
    assert rows[0]["id"] == 1


def test_download_pdf_attachment_decodes_base64(rpc: MagicMock) -> None:
    payload = base64.b64encode(b"%PDF-1.4 test").decode("ascii")
    rpc.search_read.return_value = [
        {
            "id": 7,
            "name": "guide.pdf",
            "mimetype": "application/pdf",
            "res_model": "knowledge.article",
            "res_id": 3,
            "write_date": "2026-01-01 10:00:00",
            "datas": payload,
        }
    ]

    att = download_pdf_attachment(rpc, 7)

    assert att.attachment_id == 7
    assert att.content.startswith(b"%PDF")
    assert att.citation_name.startswith("odoo-knowledge-article-7-")


@pytest.mark.asyncio
async def test_sync_pdf_attachments_indexes_via_rag_service(rpc: MagicMock) -> None:
    rpc.search_read.side_effect = [
        [{"id": 9, "name": "a.pdf", "write_date": "2026-01-02 08:00:00"}],
        [
            {
                "id": 9,
                "name": "a.pdf",
                "mimetype": "application/pdf",
                "res_model": "sale.order",
                "res_id": 1,
                "write_date": "2026-01-02 08:00:00",
                "datas": base64.b64encode(b"%PDF-1.4 x").decode("ascii"),
            }
        ],
    ]

    with patch(
        "assistant.modules.odoo_sync.service.rag_service.ingest_file",
        autospec=True,
    ) as mock_ingest:
        from assistant.modules.rag.service import IngestResult

        mock_ingest.return_value = IngestResult(file="odoo-sale-order-9-a.pdf", num_chunks=2)
        result = await sync_pdf_attachments(client=rpc, limit=5)

    assert result.scanned == 1
    assert result.indexed == 1
    mock_ingest.assert_awaited_once()
