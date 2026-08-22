"""Chroma vector store singleton."""

from pathlib import Path

import chromadb

COLLECTION_NAME = "rag_docs"
_PERSIST_DIR = Path("data/processed/chroma")


_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(_PERSIST_DIR))
    return _client


def get_collection() -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection() -> None:
    """Drop and recreate the collection. Used by local measure scripts, not by the API."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    get_collection()
