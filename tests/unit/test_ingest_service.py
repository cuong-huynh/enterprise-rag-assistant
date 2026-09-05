"""Tests for ingest submission (sync vs queue)."""

from unittest.mock import AsyncMock, patch

import pytest

from assistant.core import config
from assistant.modules.ingest.service import IngestSubmission, submit_pdf


@pytest.mark.asyncio
async def test_submit_pdf_sync() -> None:
    with patch(
        "assistant.modules.ingest.service.rag_service.ingest_file",
        new=AsyncMock(return_value=type("R", (), {"file": "a.pdf", "num_chunks": 3})()),
    ):
        result = await submit_pdf("a.pdf", b"%PDF-1.4")

    assert result == IngestSubmission(file="a.pdf", num_chunks=3, status="completed", job_id=None)


@pytest.mark.asyncio
async def test_submit_pdf_queues_when_enabled(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(config.settings, "ingest_mode", "queue")
    monkeypatch.setattr(config.settings, "redis_url", "redis://localhost:6379/0")
    monkeypatch.setattr(config.settings, "ingest_inbox_dir", tmp_path)

    with patch("assistant.modules.ingest.service.enqueue") as mock_enqueue:
        result = await submit_pdf("big.pdf", b"%PDF-1.4")

    assert result.status == "queued"
    assert result.num_chunks == 0
    assert result.job_id is not None
    mock_enqueue.assert_called_once()
    saved = list(tmp_path.glob("*_big.pdf"))
    assert len(saved) == 1
