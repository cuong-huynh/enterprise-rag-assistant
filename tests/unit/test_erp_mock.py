from pathlib import Path

import pytest

from assistant.modules.erp.mock import MockErpAdapter

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


def test_get_schema_lists_tables(ensure_mock_db: Path) -> None:
    adapter = MockErpAdapter(db_path=ensure_mock_db)
    schema = adapter.get_schema()
    assert "sale_order" in schema
    assert "stock_quant" in schema


def test_search_read_sale_orders(ensure_mock_db: Path) -> None:
    adapter = MockErpAdapter(db_path=ensure_mock_db)
    rows = adapter.search_read(
        "sale.order",
        domain=[("state", "in", ["sale", "done"])],
        fields=["name", "amount_total", "state"],
        limit=5,
    )
    assert rows
    assert set(rows[0]) == {"name", "amount_total", "state"}


def test_search_read_rejects_unknown_model(ensure_mock_db: Path) -> None:
    adapter = MockErpAdapter(db_path=ensure_mock_db)
    with pytest.raises(ValueError, match="not allowed"):
        adapter.search_read("account.move", fields=["id"])
