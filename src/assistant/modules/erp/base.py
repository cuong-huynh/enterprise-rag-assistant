"""ERP adapter interface — engine code depends on this, not on Odoo or SQLite."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ErpAdapter(ABC):
    """Read-only access to structured ERP data (Odoo live or mock SQLite)."""

    @abstractmethod
    def get_schema(self) -> str:
        """Return a human/LLM-readable schema description for allowed models."""

    @abstractmethod
    def search_read(
        self,
        model: str,
        domain: list[Any] | None = None,
        fields: list[str] | None = None,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Odoo-style record fetch. ``domain`` uses a simplified list form."""
