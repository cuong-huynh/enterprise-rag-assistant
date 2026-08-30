"""One ``search_read`` via the ERP adapter (mock or Odoo stub)."""

from __future__ import annotations

from typing import Any

from assistant.modules.erp import get_adapter
from assistant.modules.text2sql.planner import plan_search
from assistant.modules.text2sql.state import QueryState

_MAX_LIMIT = 100


def fetch(state: QueryState) -> dict[str, Any]:
    plan = plan_search(state["question"])
    if plan is None:
        return {
            "fetch_error": "Could not map the question to an allowed ERP model.",
            "rows": [],
            "models_used": [],
            "tool_steps": 0,
        }

    adapter = get_adapter()
    limit = min(plan.limit, _MAX_LIMIT)
    try:
        rows = adapter.search_read(
            plan.model,
            domain=plan.domain,
            fields=plan.fields,
            limit=limit,
        )
    except (ValueError, FileNotFoundError, NotImplementedError) as exc:
        return {
            "fetch_error": str(exc),
            "rows": [],
            "model": plan.model,
            "domain": plan.domain,
            "fields": plan.fields,
            "models_used": [],
            "tool_steps": 1,
        }

    return {
        "model": plan.model,
        "domain": plan.domain,
        "fields": plan.fields,
        "rows": rows,
        "models_used": [plan.model],
        "tool_steps": 1,
        "fetch_error": "",
    }
