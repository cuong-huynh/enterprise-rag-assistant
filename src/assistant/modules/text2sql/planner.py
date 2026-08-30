"""Map a natural-language question to one ``search_read`` call (mock-safe).

Real LLM planning is P3 stretch; tests and CI stay on this rule table so
``LLM_MODE=mock`` still hits the adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchPlan:
    model: str
    domain: list[Any]
    fields: list[str]
    limit: int = 100


def plan_search(question: str) -> SearchPlan | None:
    """Return a single read plan, or None if the question does not map."""
    q = question.lower()

    if any(k in q for k in ("stock", "tồn", "inventory", "warehouse", "quant")):
        return SearchPlan(
            model="stock.quant",
            domain=[],
            fields=["product_id", "location_name", "quantity", "reserved_quantity"],
        )
    if any(k in q for k in ("product", "sản phẩm", "sku", "barcode")):
        return SearchPlan(
            model="product.product",
            domain=[],
            fields=["name", "default_code", "list_price"],
            limit=30,
        )
    if any(k in q for k in ("partner", "customer", "khách", "supplier", "ncc", "vendor")):
        return SearchPlan(
            model="res.partner",
            domain=[],
            fields=["name", "email", "is_company"],
            limit=30,
        )
    if any(k in q for k in ("line", "order line", "dòng đơn")):
        return SearchPlan(
            model="sale.order.line",
            domain=[],
            fields=["order_id", "name", "product_uom_qty", "price_subtotal"],
        )
    if any(
        k in q
        for k in (
            "sale",
            "order",
            "đơn",
            "doanh thu",
            "revenue",
            "confirmed",
            "amount",
        )
    ):
        domain: list[Any] = []
        if any(k in q for k in ("sale", "confirmed", "done", "doanh thu", "revenue")):
            domain = [("state", "in", ["sale", "done"])]
        return SearchPlan(
            model="sale.order",
            domain=domain,
            fields=["name", "state", "amount_total", "date_order"],
        )
    return None
