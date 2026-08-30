"""Public gate for the structured-query engine. api/ imports only from here."""

from __future__ import annotations

from dataclasses import dataclass, field

from assistant.modules.text2sql.graph import get_compiled_graph


@dataclass
class DataAnswer:
    answer: str
    blocked: bool
    block_reason: str | None
    models_used: list[str] = field(default_factory=list)
    tool_steps: int = 0


async def ask(question: str) -> DataAnswer:
    """Run guardrail → search_read → response. Numbers come from the adapter."""
    graph = get_compiled_graph()
    result = graph.invoke({"question": question})
    blocked = bool(result.get("blocked"))
    reason = result.get("block_reason") or None
    if not blocked:
        reason = None
    return DataAnswer(
        answer=result.get("answer") or "",
        blocked=blocked,
        block_reason=reason,
        models_used=list(result.get("models_used") or []),
        tool_steps=int(result.get("tool_steps") or 0),
    )
