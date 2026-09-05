"""Compile the agentic RAG graph.

Flow: retrieve → critique → (retrieve | generate) → END
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langgraph.graph import END, START, StateGraph

from assistant.modules.rag.orchestration.nodes.critique import critique
from assistant.modules.rag.orchestration.nodes.generate import generate
from assistant.modules.rag.orchestration.nodes.retrieve import retrieve
from assistant.modules.rag.orchestration.state import RagState


def _after_critique(state: RagState) -> Literal["retrieve", "generate"]:
    if state.get("need_more"):
        return "retrieve"
    return "generate"


def build_graph() -> StateGraph:
    graph = StateGraph(RagState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("critique", critique)
    graph.add_node("generate", generate)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "critique")
    graph.add_conditional_edges(
        "critique",
        _after_critique,
        {"retrieve": "retrieve", "generate": "generate"},
    )
    graph.add_edge("generate", END)
    return graph


@lru_cache
def get_compiled_graph():
    return build_graph().compile()
