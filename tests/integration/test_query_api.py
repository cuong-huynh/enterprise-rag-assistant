"""Integration tests for POST /query."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from assistant.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "data" / "mock_odoo.sqlite"


@pytest.fixture
def app():
    return create_app()


@pytest.fixture(scope="module")
def ensure_mock_db() -> Path:
    if not DB_PATH.exists():
        import sys

        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from generate_mock_odoo import generate

        generate()
    return DB_PATH


@pytest.mark.asyncio
async def test_query_blocks_write(app, ensure_mock_db: Path) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/query", json={"question": "UPDATE sale_order SET state='draft'"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["blocked"] is True
    assert data["tool_steps"] == 0


@pytest.mark.asyncio
async def test_query_sale_orders(app, ensure_mock_db: Path) -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/query",
            json={"question": "How many sale orders are in state sale?"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["blocked"] is False
    assert data["models_used"] == ["sale.order"]
    assert data["tool_steps"] == 1
    assert "sale.order" in data["answer"]
