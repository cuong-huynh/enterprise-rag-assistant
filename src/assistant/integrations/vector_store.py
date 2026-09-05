"""Chroma vector store singleton."""

import chromadb

from assistant.core.config import settings

COLLECTION_NAME = "rag_docs"

_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        persist = settings.chroma_persist_dir
        persist.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(persist))
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


def delete_chunks_by_source(source: str) -> int:
    """Remove all chunks for a source filename before re-ingest."""
    if not source:
        return 0
    collection = get_collection()
    existing = collection.get(where={"source": source}, include=[])
    ids = list(existing.get("ids") or [])
    if not ids:
        return 0
    collection.delete(ids=ids)
    return len(ids)
