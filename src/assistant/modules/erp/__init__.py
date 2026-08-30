"""ERP adapters — mock SQLite (P3) and Odoo JSON-RPC stub (P6)."""

from assistant.core.config import settings
from assistant.modules.erp.base import ErpAdapter
from assistant.modules.erp.mock import MockErpAdapter
from assistant.modules.erp.odoo import OdooErpAdapter


def get_adapter() -> ErpAdapter:
    """Return the adapter selected by ``erp_mode`` (mock | odoo)."""
    if settings.erp_mode == "odoo":
        return OdooErpAdapter()
    return MockErpAdapter()


__all__ = ["ErpAdapter", "MockErpAdapter", "OdooErpAdapter", "get_adapter"]
