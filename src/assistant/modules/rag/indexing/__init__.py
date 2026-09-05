"""Indexing stage: embed chunks and persist to Chroma."""

from assistant.modules.rag.indexing.store import embed_and_store

__all__ = ["embed_and_store"]
