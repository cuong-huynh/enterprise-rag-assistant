"""Graph state for the structured-query engine."""

from __future__ import annotations

from typing import Any, TypedDict


class QueryState(TypedDict, total=False):
    question: str
    blocked: bool
    block_reason: str
    model: str
    domain: list[Any]
    fields: list[str]
    rows: list[dict[str, Any]]
    fetch_error: str
    answer: str
    models_used: list[str]
    tool_steps: int
