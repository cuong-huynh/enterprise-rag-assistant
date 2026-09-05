"""Unit tests for embedding_client mock mode."""

from assistant.integrations.embedding_client import EMBED_DIM, embed_documents, embed_query


def test_mock_embed_dimension() -> None:
    vectors = embed_documents(["hello", "world"])
    assert len(vectors) == 2
    assert len(vectors[0]) == EMBED_DIM
    assert len(vectors[1]) == EMBED_DIM


def test_mock_embed_deterministic() -> None:
    a = embed_query("cycle count warehouse")
    b = embed_query("cycle count warehouse")
    c = embed_query("different text")
    assert a == b
    assert a != c


def test_mock_embed_empty() -> None:
    assert embed_documents([]) == []
