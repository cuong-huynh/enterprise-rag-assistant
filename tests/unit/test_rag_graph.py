"""Unit tests for agentic RAG graph multi-step retrieve."""

from unittest.mock import AsyncMock, patch

import pytest

from assistant.modules.rag.ingestion.chunk import Document
from assistant.modules.rag.orchestration.graph import get_compiled_graph


@pytest.fixture(autouse=True)
def _clear_graph_cache() -> None:
    get_compiled_graph.cache_clear()
    yield
    get_compiled_graph.cache_clear()


@pytest.mark.asyncio
async def test_graph_retries_when_first_retrieve_empty() -> None:
    doc = Document(text="cycle count steps", source="sop.pdf", page=0, chunk_id="x1")
    call_count = 0

    def fake_retrieve(query: str, k: int = 5) -> list[Document]:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return []
        return [doc]

    with (
        patch(
            "assistant.modules.rag.orchestration.nodes.retrieve.retrieve_with_query",
            side_effect=fake_retrieve,
        ),
        patch(
            "assistant.modules.rag.orchestration.nodes.generate.generate_answer",
            new=AsyncMock(return_value=type("R", (), {"answer": "ok", "sources": ["sop.pdf p.1"]})()),
        ),
    ):
        graph = get_compiled_graph()
        final = await graph.ainvoke({"question": "kiểm kê xoay vòng", "top_k": 3})

    assert call_count >= 2
    assert final.get("answer") == "ok"
    assert final.get("sources") == ["sop.pdf p.1"]
