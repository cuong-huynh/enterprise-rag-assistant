"""SQLite mock Odoo adapter for local P3 development."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from assistant.core.config import settings
from assistant.modules.erp.base import ErpAdapter

MODEL_TABLE = {
    "res.partner": "res_partner",
    "res_partner": "res_partner",
    "product.product": "product_product",
    "product_product": "product_product",
    "sale.order": "sale_order",
    "sale_order": "sale_order",
    "sale.order.line": "sale_order_line",
    "sale_order_line": "sale_order_line",
    "stock.quant": "stock_quant",
    "stock_quant": "stock_quant",
}

TABLE_COLUMNS: dict[str, list[str]] = {
    "res_partner": [
        "id",
        "name",
        "email",
        "phone",
        "is_company",
        "customer_rank",
        "supplier_rank",
        "active",
        "create_date",
    ],
    "product_product": [
        "id",
        "default_code",
        "barcode",
        "name",
        "list_price",
        "standard_price",
        "type",
        "active",
    ],
    "sale_order": [
        "id",
        "name",
        "partner_id",
        "date_order",
        "state",
        "amount_total",
        "user_id",
        "company_id",
    ],
    "sale_order_line": [
        "id",
        "order_id",
        "product_id",
        "name",
        "product_uom_qty",
        "price_unit",
        "price_subtotal",
        "discount",
    ],
    "stock_quant": [
        "id",
        "product_id",
        "location_id",
        "location_name",
        "quantity",
        "reserved_quantity",
        "in_date",
    ],
}


def _resolve_table(model: str) -> str:
    table = MODEL_TABLE.get(model)
    if table is None:
        raise ValueError(f"Model not allowed: {model}")
    return table


def _compile_domain(domain: list[Any] | None) -> tuple[str, list[Any]]:
    """Support a small Odoo-like subset: ``[('field', op, value), ...]`` with AND."""
    if not domain:
        return "", []

    clauses: list[str] = []
    params: list[Any] = []
    for term in domain:
        if not isinstance(term, (list, tuple)) or len(term) != 3:
            raise ValueError(f"Invalid domain term: {term!r}")
        field, op, value = term
        if op == "=":
            clauses.append(f"{field} = ?")
            params.append(value)
        elif op == "!=":
            clauses.append(f"{field} != ?")
            params.append(value)
        elif op == ">":
            clauses.append(f"{field} > ?")
            params.append(value)
        elif op == ">=":
            clauses.append(f"{field} >= ?")
            params.append(value)
        elif op == "<":
            clauses.append(f"{field} < ?")
            params.append(value)
        elif op == "<=":
            clauses.append(f"{field} <= ?")
            params.append(value)
        elif op == "in":
            if not value:
                clauses.append("0 = 1")
            else:
                placeholders = ", ".join("?" for _ in value)
                clauses.append(f"{field} IN ({placeholders})")
                params.extend(value)
        elif op == "ilike":
            clauses.append(f"{field} LIKE ?")
            params.append(f"%{value}%")
        else:
            raise ValueError(f"Unsupported domain operator: {op}")
    return " AND ".join(clauses), params


class MockErpAdapter(ErpAdapter):
    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or settings.mock_odoo_db_path

    def _connect(self) -> sqlite3.Connection:
        if not self._db_path.exists():
            raise FileNotFoundError(
                f"Mock Odoo DB not found at {self._db_path}. "
                "Run: uv run python scripts/generate_mock_odoo.py"
            )
        conn = sqlite3.connect(f"file:{self._db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def get_schema(self) -> str:
        lines = ["Mock Odoo SQLite schema (read-only):"]
        for table, columns in TABLE_COLUMNS.items():
            lines.append(f"- {table}({', '.join(columns)})")
        return "\n".join(lines)

    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        table = _resolve_table(model)
        allowed = TABLE_COLUMNS[table]
        selected = fields or allowed
        unknown = [f for f in selected if f not in allowed]
        if unknown:
            raise ValueError(f"Unknown fields for {model}: {unknown}")

        where_sql, params = _compile_domain(domain)
        sql = f"SELECT {', '.join(selected)} FROM {table}"
        if where_sql:
            sql += f" WHERE {where_sql}"
        sql += " LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
