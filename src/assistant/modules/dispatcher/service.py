"""Public gate for the dispatcher. api/ imports only from here."""

from __future__ import annotations

from dataclasses import dataclass, field

from assistant.modules.dispatcher.classifier import RouteDecision, classify_route
from assistant.modules.rag import service as rag_service
from assistant.modules.text2sql import service as text2sql_service


@dataclass
class ChatAnswer:
    answer: str
    route: str
    reason: str
    sources: list[str] = field(default_factory=list)
    blocked: bool = False
    block_reason: str | None = None
    models_used: list[str] = field(default_factory=list)
    tool_steps: int = 0


def _merge_hybrid(rag_answer: str, rag_sources: list[str], data_answer: str) -> str:
    source_line = ", ".join(rag_sources) if rag_sources else "none"
    return (
        "[Documents]\n"
        f"{rag_answer}\n\n"
        "[Data]\n"
        f"{data_answer}\n\n"
        f"(Hybrid: citations {source_line})"
    )


async def chat(question: str) -> ChatAnswer:
    """Classify the question and delegate to the right engine(s)."""
    decision = classify_route(question)

    if decision.route == "rag":
        rag = await rag_service.ask(question)
        return ChatAnswer(
            answer=rag.answer,
            route="rag",
            reason=decision.reason,
            sources=list(rag.sources),
        )

    if decision.route == "data":
        data = await text2sql_service.ask(question)
        return ChatAnswer(
            answer=data.answer,
            route="data",
            reason=decision.reason,
            blocked=data.blocked,
            block_reason=data.block_reason,
            models_used=list(data.models_used),
            tool_steps=data.tool_steps,
        )

    rag = await rag_service.ask(question)
    data = await text2sql_service.ask(question)
    return ChatAnswer(
        answer=_merge_hybrid(rag.answer, list(rag.sources), data.answer),
        route="hybrid",
        reason=decision.reason,
        sources=list(rag.sources),
        blocked=data.blocked,
        block_reason=data.block_reason,
        models_used=list(data.models_used),
        tool_steps=data.tool_steps,
    )


def classify(question: str) -> RouteDecision:
    """Expose routing only — used by eval harness without calling engines."""
    return classify_route(question)
