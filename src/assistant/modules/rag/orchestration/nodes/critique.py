"""Critique node — decide whether another retrieve step is needed."""

from __future__ import annotations

from assistant.modules.rag.config import load_rag_config
from assistant.modules.rag.orchestration.state import RagState


def critique(state: RagState) -> RagState:
    cfg = load_rag_config()
    max_steps = int(cfg["max_retrieve_steps"])
    docs = list(state.get("docs") or [])
    steps = int(state.get("retrieve_steps") or 0)

    if docs:
        return {"need_more": False}
    if steps >= max_steps:
        return {"need_more": False}
    return {"need_more": True}
