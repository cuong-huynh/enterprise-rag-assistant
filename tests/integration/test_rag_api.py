"""Integration tests for /ask and /ingest endpoints."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from assistant.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_ask_returns_answer_and_sources(app) -> None:
    from assistant.modules.rag.generate import RagAnswer

    mock_answer = RagAnswer(answer="Mocked answer", sources=["doc.pdf p.1"])

    with patch("assistant.modules.rag.service.ask", new=AsyncMock(return_value=mock_answer)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/ask", json={"question": "What is Odoo?"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "Mocked answer"
    assert data["sources"] == ["doc.pdf p.1"]
    assert "mode" in data


@pytest.mark.asyncio
async def test_ingest_rejects_non_pdf(app) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/ingest",
            files={"file": ("note.txt", io.BytesIO(b"hello"), "text/plain")},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_ingest_accepts_pdf(app) -> None:
    from assistant.modules.rag.service import IngestResult

    mock_result = IngestResult(file="sample.pdf", num_chunks=5)

    with patch(
        "assistant.modules.rag.service.ingest_file", new=AsyncMock(return_value=mock_result)
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/ingest",
                files={"file": ("sample.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["num_chunks"] == 5
