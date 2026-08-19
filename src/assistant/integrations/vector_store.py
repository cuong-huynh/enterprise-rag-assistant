"""Chroma vector store singleton."""

from functools import lru_cache
from pathlib import Path

import chromadb

COLLECTION_NAME = "rag_docs"
_PERSIST_DIR = Path("data/processed/chroma")


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    _PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(_PERSIST_DIR))


def get_collection() -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
