"""Live Odoo XML-RPC adapter — ``search_read`` via ``execute_kw``."""

from __future__ import annotations

from typing import Any

from assistant.core.config import settings
from assistant.integrations.odoo_rpc import OdooRpcClient
from assistant.modules.erp.base import ErpAdapter
from assistant.modules.erp.mock import MODEL_TABLE

ALLOWED_MODELS = frozenset(MODEL_TABLE)

# Fields exposed to the planner/LLM (Odoo-native names).
ODOO_FIELDS: dict[str, list[str]] = {
    "res.partner": [
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
    "product.product": [
        "id",
        "default_code",
        "barcode",
        "name",
        "list_price",
        "standard_price",
        "type",
        "active",
    ],
    "sale.order": [
        "id",
        "name",
        "partner_id",
        "date_order",
        "state",
        "amount_total",
        "user_id",
        "company_id",
    ],
    "sale.order.line": [
        "id",
        "order_id",
        "product_id",
        "name",
        "product_uom_qty",
        "price_unit",
        "price_subtotal",
        "discount",
    ],
    "stock.quant": [
        "id",
        "product_id",
        "location_id",
        "quantity",
        "reserved_quantity",
        "in_date",
    ],
}

# Mock SQLite uses ``location_name``; on live Odoo read ``location_id`` instead.
_FIELD_ALIASES: dict[str, str] = {
    "location_name": "location_id",
}


def _normalize_model(model: str) -> str:
    table = MODEL_TABLE.get(model)
    if table is None:
        raise ValueError(f"Model not allowed: {model}")
    for key in ODOO_FIELDS:
        if MODEL_TABLE.get(key) == table:
            return key
    raise ValueError(f"Model not allowed: {model}")


def _prepare_fields(model: str, fields: list[str] | None) -> tuple[list[str], dict[str, str]]:
    allowed = ODOO_FIELDS[model]
    selected = fields or allowed
    rpc_fields: list[str] = []
    rename_back: dict[str, str] = {}
    for field in selected:
        if field in allowed:
            rpc_fields.append(field)
            continue
        alias = _FIELD_ALIASES.get(field)
        if alias and alias in allowed:
            if alias not in rpc_fields:
                rpc_fields.append(alias)
            rename_back[alias] = field
            continue
        raise ValueError(f"Unknown fields for {model}: {[field]}")
    return rpc_fields, rename_back


def _rename_rows(rows: list[dict[str, Any]], rename_back: dict[str, str]) -> list[dict[str, Any]]:
    if not rename_back:
        return rows
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        for rpc_field, requested in rename_back.items():
            if rpc_field in item:
                value = item.pop(rpc_field)
                if requested == "location_name" and isinstance(value, (list, tuple)) and len(value) >= 2:
                    item[requested] = value[1]
                else:
                    item[requested] = value
        out.append(item)
    return out


class OdooErpAdapter(ErpAdapter):
    """Read-only Odoo access through XML-RPC ``search_read``."""

    def __init__(
        self,
        *,
        url: str | None = None,
        db: str | None = None,
        username: str | None = None,
        password: str | None = None,
        client: OdooRpcClient | None = None,
    ) -> None:
        self._rpc = client or OdooRpcClient(
            url=url,
            db=db,
            username=username,
            password=password,
        )

    def get_schema(self) -> str:
        lines = [f"Odoo live schema (read-only, db={self._rpc.db}):"]
        for model, columns in ODOO_FIELDS.items():
            lines.append(f"- {model}({', '.join(columns)})")
        return "\n".join(lines)

    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        normalized = _normalize_model(model)
        if normalized not in ALLOWED_MODELS:
            raise ValueError(f"Model not allowed: {model}")

        rpc_fields, rename_back = _prepare_fields(normalized, fields)
        safe_limit = min(max(limit, 1), 100)

        rows = self._rpc.search_read(
            normalized,
            domain or [],
            fields=rpc_fields,
            limit=safe_limit,
        )
        return _rename_rows(rows, rename_back)
