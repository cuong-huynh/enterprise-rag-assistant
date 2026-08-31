"""Retrieve top-k relevant chunks for a question."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from assistant.integrations.vector_store import get_collection
from assistant.modules.rag.chunk import Document
from assistant.modules.rag.index import embed_texts

_EXPAND_PATH = Path(__file__).resolve().parents[4] / "configs" / "prompts" / "rag_expand.yaml"


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


def retrieve_top_k(question: str, k: int = 5) -> list[Document]:
    """Return the top-k most relevant chunks for the given question."""
    query_embedding = embed_texts([expand_query(question)])[0]
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas"],
    )

    docs: list[Document] = []
    for text, meta, chunk_id in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0],
    ):
        docs.append(
            Document(
                text=text,
                source=meta["source"],
                page=meta["page"],
                chunk_id=chunk_id,
            )
        )
    return docs
