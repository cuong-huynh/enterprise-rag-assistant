"""Graph state for the agentic RAG engine."""

from __future__ import annotations

from typing import TypedDict

from assistant.modules.rag.ingestion.chunk import Document


class RagState(TypedDict, total=False):
    question: str
    query: str
    top_k: int
    docs: list[Document]
    retrieve_steps: int
    need_more: bool
    answer: str
    sources: list[str]
