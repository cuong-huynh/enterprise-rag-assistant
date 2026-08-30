"""Turn rows (or a block reason) into a short answer. Numbers come from rows, not the LLM."""

from __future__ import annotations

from typing import Any

from assistant.modules.text2sql.state import QueryState


def _format_rows(model: str, rows: list[dict[str, Any]]) -> str:
    n = len(rows)
    if n == 0:
        return f"No records found on {model}."

    if model == "sale.order" and any("amount_total" in r for r in rows):
        total = sum(float(r.get("amount_total") or 0) for r in rows)
        return (
            f"Found {n} sale.order row(s). "
            f"Sum of amount_total = {round(total, 2)} "
            f"(from mock ERP search_read)."
        )
    if model == "stock.quant" and any("quantity" in r for r in rows):
        qty = sum(float(r.get("quantity") or 0) for r in rows)
        return (
            f"Found {n} stock.quant row(s). "
            f"Sum of quantity = {round(qty, 2)} "
            f"(from mock ERP search_read)."
        )

    sample = rows[0]
    preview = ", ".join(f"{k}={v}" for k, v in list(sample.items())[:4])
    return f"Found {n} {model} row(s). Example: {preview}."


def response(state: QueryState) -> dict[str, Any]:
    if state.get("blocked"):
        reason = state.get("block_reason") or "Blocked by guardrail."
        return {"answer": reason}

    err = state.get("fetch_error") or ""
    if err:
        return {"answer": err}

    model = state.get("model") or "unknown"
    rows = state.get("rows") or []
    return {"answer": _format_rows(model, rows)}
