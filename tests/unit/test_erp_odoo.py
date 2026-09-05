from unittest.mock import MagicMock

import pytest

from assistant.modules.erp.odoo import OdooErpAdapter


@pytest.fixture
def rpc() -> MagicMock:
    mock = MagicMock()
    mock.db = "testdb"
    return mock


@pytest.fixture
def adapter(rpc: MagicMock) -> OdooErpAdapter:
    return OdooErpAdapter(client=rpc)


def test_get_schema_lists_odoo_models(adapter: OdooErpAdapter) -> None:
    schema = adapter.get_schema()
    assert "sale.order" in schema
    assert "stock.quant" in schema


def test_search_read_rejects_unknown_model(adapter: OdooErpAdapter) -> None:
    with pytest.raises(ValueError, match="not allowed"):
        adapter.search_read("account.move", fields=["id"])


def test_search_read_calls_rpc_search_read(rpc: MagicMock, adapter: OdooErpAdapter) -> None:
    rpc.search_read.return_value = [
        {"name": "SO001", "amount_total": 100.0, "state": "sale"},
    ]

    rows = adapter.search_read(
        "sale.order",
        domain=[("state", "in", ["sale", "done"])],
        fields=["name", "amount_total", "state"],
        limit=5,
    )

    assert rows == [{"name": "SO001", "amount_total": 100.0, "state": "sale"}]
    rpc.search_read.assert_called_once_with(
        "sale.order",
        [("state", "in", ["sale", "done"])],
        fields=["name", "amount_total", "state"],
        limit=5,
    )


def test_search_read_maps_location_name_alias(rpc: MagicMock, adapter: OdooErpAdapter) -> None:
    rpc.search_read.return_value = [
        {
            "product_id": [10, "Desk"],
            "location_id": [5, "WH/Stock"],
            "quantity": 12.0,
            "reserved_quantity": 0.0,
        },
    ]

    rows = adapter.search_read(
        "stock.quant",
        fields=["product_id", "location_name", "quantity", "reserved_quantity"],
        limit=10,
    )

    assert rows[0]["location_name"] == "WH/Stock"
    rpc.search_read.assert_called_once_with(
        "stock.quant",
        [],
        fields=["product_id", "location_id", "quantity", "reserved_quantity"],
        limit=10,
    )
