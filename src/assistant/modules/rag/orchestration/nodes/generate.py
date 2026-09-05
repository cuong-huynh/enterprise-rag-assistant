"""Generate node — LLM answer with citations."""

from __future__ import annotations

from assistant.modules.rag.generation.answer import generate_answer
from assistant.modules.rag.orchestration.state import RagState


async def generate(state: RagState) -> RagState:
    question = state.get("question") or ""
    docs = list(state.get("docs") or [])
    result = await generate_answer(question, docs)
    return {
        "answer": result.answer,
        "sources": result.sources,
    }
