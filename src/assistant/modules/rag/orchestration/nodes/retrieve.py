"""Retrieve node — embed query and fetch Chroma top-k."""

from __future__ import annotations

from assistant.modules.rag.config import load_rag_config
from assistant.modules.rag.orchestration.state import RagState
from assistant.modules.rag.retrieval.search import expand_query, retrieve_with_query


def _dedupe_docs(existing: list, new: list) -> list:
    seen = {d.chunk_id for d in existing}
    merged = list(existing)
    for doc in new:
        if doc.chunk_id not in seen:
            seen.add(doc.chunk_id)
            merged.append(doc)
    return merged


def _pick_query(state: RagState) -> str:
    question = state.get("question") or ""
    steps = int(state.get("retrieve_steps") or 0)
    if steps == 0:
        return expand_query(question)
    if steps == 1:
        return question.strip()
    return expand_query(question)


def retrieve(state: RagState) -> RagState:
    cfg = load_rag_config()
    top_k = int(state.get("top_k") or cfg["top_k"])
    query = state.get("query") or _pick_query(state)
    hits = retrieve_with_query(query, k=top_k)
    prior = list(state.get("docs") or [])
    merged = _dedupe_docs(prior, hits)
    steps = int(state.get("retrieve_steps") or 0) + 1
    return {
        "query": query,
        "docs": merged,
        "retrieve_steps": steps,
    }
