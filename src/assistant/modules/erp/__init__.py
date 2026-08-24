"""ERP adapters — mock SQLite (P3) and Odoo JSON-RPC stub (P6)."""

from assistant.modules.erp.base import ErpAdapter
from assistant.modules.erp.mock import MockErpAdapter
from assistant.modules.erp.odoo import OdooErpAdapter

__all__ = ["ErpAdapter", "MockErpAdapter", "OdooErpAdapter"]
