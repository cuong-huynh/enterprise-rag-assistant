"""Retrieval stage: vector search and query expansion."""

from assistant.modules.rag.retrieval.search import (
    expand_query,
    retrieve_top_k,
    retrieve_with_query,
)

__all__ = ["expand_query", "retrieve_top_k", "retrieve_with_query"]
