"""Integration tests for POST /chat and the chat page."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from assistant.main import create_app
from assistant.modules.rag.generation.answer import RagAnswer
from assistant.modules.text2sql.service import DataAnswer


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_chat_page_served(app) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert "Enterprise Assistant" in resp.text


@pytest.mark.asyncio
async def test_chat_routes_to_data(app) -> None:
    mock_data = DataAnswer(
        answer="3 orders",
        blocked=False,
        block_reason=None,
        models_used=["sale.order"],
        tool_steps=1,
    )
    with patch(
        "assistant.modules.dispatcher.service.text2sql_service.ask",
        new=AsyncMock(return_value=mock_data),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/chat",
                json={"question": "How many confirmed sale orders?"},
            )
    assert resp.status_code == 200
    body = resp.json()
    assert body["route"] == "data"
    assert body["answer"] == "3 orders"
    assert body["models_used"] == ["sale.order"]


@pytest.mark.asyncio
async def test_chat_routes_to_rag(app) -> None:
    mock_rag = RagAnswer(answer="Follow the SOP.", sources=["warehouse_sop.pdf p.1"])
    with patch(
        "assistant.modules.dispatcher.service.rag_service.ask",
        new=AsyncMock(return_value=mock_rag),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/chat",
                json={"question": "What are the steps to perform a cycle count?"},
            )
    assert resp.status_code == 200
    body = resp.json()
    assert body["route"] == "rag"
    assert body["sources"] == ["warehouse_sop.pdf p.1"]


@pytest.mark.asyncio
async def test_chat_hybrid_merges_engines(app) -> None:
    mock_rag = RagAnswer(answer="Doc part.", sources=["guide.pdf p.2"])
    mock_data = DataAnswer(
        answer="5 orders",
        blocked=False,
        block_reason=None,
        models_used=["sale.order"],
        tool_steps=1,
    )
    with (
        patch(
            "assistant.modules.dispatcher.service.rag_service.ask",
            new=AsyncMock(return_value=mock_rag),
        ),
        patch(
            "assistant.modules.dispatcher.service.text2sql_service.ask",
            new=AsyncMock(return_value=mock_data),
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/chat",
                json={"question": "Compare return policy with confirmed sale order revenue."},
            )
    assert resp.status_code == 200
    body = resp.json()
    assert body["route"] == "hybrid"
    assert "[Documents]" in body["answer"]
    assert "[Data]" in body["answer"]
    assert "Doc part." in body["answer"]
    assert "5 orders" in body["answer"]
