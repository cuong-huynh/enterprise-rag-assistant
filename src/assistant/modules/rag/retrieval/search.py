"""Retrieve top-k relevant chunks for a question."""

from functools import lru_cache
from typing import Any

import yaml

from assistant.integrations.embedding_client import embed_query
from assistant.integrations.vector_store import get_collection
from assistant.modules.rag.config import repo_root
from assistant.modules.rag.ingestion.chunk import Document

_EXPAND_PATH = repo_root() / "configs" / "prompts" / "rag_expand.yaml"


@lru_cache
def _load_expand() -> list[dict[str, Any]]:
    if not _EXPAND_PATH.exists():
        return []
    with _EXPAND_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return list(data.get("aliases") or [])


def expand_query(question: str) -> str:
    """Append English SOP terms when the question contains known Vietnamese phrases."""
    q = question.strip()
    lower = q.lower()
    extra: list[str] = []
    for row in _load_expand():
        match = str(row.get("match") or "").lower()
        term = str(row.get("expand") or "").strip()
        if match and term and match in lower:
            if term.lower() in lower:
                continue
            if term.lower() not in extra:
                extra.append(term)
    if not extra:
        return q
    return f"{q} {' '.join(extra)}"


def _rows_to_documents(
    texts: list[str],
    metas: list[dict[str, Any]],
    ids: list[str],
) -> list[Document]:
    docs: list[Document] = []
    for text, meta, chunk_id in zip(texts, metas, ids, strict=True):
        docs.append(
            Document(
                text=text,
                source=str(meta.get("source") or ""),
                page=int(meta.get("page") or 0),
                chunk_id=chunk_id,
                doc_id=str(meta.get("doc_id") or ""),
                ingested_at=str(meta.get("ingested_at") or ""),
            )
        )
    return docs


def retrieve_with_query(query: str, k: int = 5) -> list[Document]:
    """Return the top-k most relevant chunks for the given query string."""
    query_embedding = embed_query(query)
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas"],
    )

    if not results["documents"] or not results["documents"][0]:
        return []

    return _rows_to_documents(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0],
    )


def retrieve_top_k(question: str, k: int = 5, *, expand: bool = True) -> list[Document]:
    """Return the top-k most relevant chunks for the given question."""
    query = expand_query(question) if expand else question.strip()
    return retrieve_with_query(query, k=k)
