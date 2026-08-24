"""Live Odoo JSON-RPC adapter — stub until P6."""

from __future__ import annotations

from typing import Any

from assistant.modules.erp.base import ErpAdapter


class OdooErpAdapter(ErpAdapter):
    def get_schema(self) -> str:
        raise NotImplementedError("Odoo JSON-RPC adapter is planned for P6.")

    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Odoo JSON-RPC adapter is planned for P6.")
