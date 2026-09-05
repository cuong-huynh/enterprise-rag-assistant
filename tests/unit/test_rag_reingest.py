"""Unit tests for re-ingest lifecycle (delete-by-source)."""

from unittest.mock import MagicMock, patch

import pytest

from assistant.modules.rag.indexing.store import embed_and_store
from assistant.modules.rag.ingestion.chunk import Document


@pytest.fixture
def mock_collection() -> MagicMock:
    collection = MagicMock()
    collection.get.return_value = {"ids": ["old-chunk-1", "old-chunk-2"]}
    return collection


@patch("assistant.modules.rag.indexing.store.embed_documents")
@patch("assistant.modules.rag.indexing.store.get_collection")
@patch("assistant.modules.rag.indexing.store.delete_chunks_by_source")
def test_reingest_deletes_old_source(
    mock_delete: MagicMock,
    mock_get_collection: MagicMock,
    mock_embed: MagicMock,
    mock_collection: MagicMock,
) -> None:
    mock_get_collection.return_value = mock_collection
    mock_embed.return_value = [[0.1] * 768]

    docs = [
        Document(
            text="chunk one",
            source="manual.pdf",
            page=0,
            chunk_id="abc",
            doc_id="doc-1",
            ingested_at="2026-01-01T00:00:00+00:00",
        )
    ]
    count = embed_and_store(docs)

    mock_delete.assert_called_once_with("manual.pdf")
    mock_collection.upsert.assert_called_once()
    assert count == 1
