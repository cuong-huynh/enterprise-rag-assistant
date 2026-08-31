from pathlib import Path

import pytest

from assistant.modules.erp.mock import MockErpAdapter
from assistant.modules.text2sql import service as text2sql_service

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "data" / "mock_odoo.sqlite"


@pytest.fixture(scope="module")
def ensure_mock_db() -> Path:
    if not DB_PATH.exists():
        import sys

        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from generate_mock_odoo import generate

        generate()
    return DB_PATH


@pytest.mark.asyncio
async def test_ask_sale_orders_hits_search_read(ensure_mock_db: Path) -> None:
    adapter = MockErpAdapter(db_path=ensure_mock_db)
    expected = adapter.search_read(
        "sale.order",
        domain=[("state", "in", ["sale", "done"])],
        fields=["name", "state", "amount_total", "date_order"],
        limit=100,
    )

    result = await text2sql_service.ask("How many confirmed sale orders are there?")

    assert not result.blocked
    assert result.tool_steps == 1
    assert result.models_used == ["sale.order"]
    assert str(len(expected)) in result.answer
    assert "amount_total" in result.answer


@pytest.mark.asyncio
async def test_ask_confirmed_orders_vietnamese_same_filter(ensure_mock_db: Path) -> None:
    adapter = MockErpAdapter(db_path=ensure_mock_db)
    expected = adapter.search_read(
        "sale.order",
        domain=[("state", "in", ["sale", "done"])],
        fields=["name", "state", "amount_total", "date_order"],
        limit=100,
    )

    result = await text2sql_service.ask("Có bao nhiêu đơn hàng đã được xác nhận?")

    assert not result.blocked
    assert str(len(expected)) in result.answer
