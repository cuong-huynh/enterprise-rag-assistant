"""Unit tests for RAG chunking."""

from assistant.modules.rag.chunk import chunk_texts


def test_chunk_splits_long_text() -> None:
    long_text = "word " * 300  # ~1500 chars → should split into multiple chunks
    pages = [(long_text, {"source": "test.pdf", "page": 0})]
    docs = chunk_texts(pages)
    assert len(docs) > 1
    for doc in docs:
        assert doc.source == "test.pdf"
        assert doc.page == 0
        assert doc.chunk_id


def test_chunk_empty_pages() -> None:
    docs = chunk_texts([])
    assert docs == []


def test_chunk_dedup_ids() -> None:
    text = "Hello world this is a test document."
    pages = [(text, {"source": "a.pdf", "page": 0})]
    docs1 = chunk_texts(pages)
    docs2 = chunk_texts(pages)
    assert docs1[0].chunk_id == docs2[0].chunk_id
