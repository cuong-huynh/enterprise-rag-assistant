"""Compile the structured-query graph.

v1 slice (P3): guardrail → one search_read → response.
ReAct loop + critique stay out until this path is green.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from langgraph.graph import END, START, StateGraph

from assistant.modules.text2sql.nodes.fetch import fetch
from assistant.modules.text2sql.nodes.guardrail import guardrail
from assistant.modules.text2sql.nodes.response import response
from assistant.modules.text2sql.state import QueryState


def _after_guardrail(state: QueryState) -> Literal["fetch", "response"]:
    if state.get("blocked"):
        return "response"
    return "fetch"


def build_graph() -> StateGraph:
    graph = StateGraph(QueryState)
    graph.add_node("guardrail", guardrail)
    graph.add_node("fetch", fetch)
    graph.add_node("response", response)

    graph.add_edge(START, "guardrail")
    graph.add_conditional_edges(
        "guardrail",
        _after_guardrail,
        {"fetch": "fetch", "response": "response"},
    )
    graph.add_edge("fetch", "response")
    graph.add_edge("response", END)
    return graph


@lru_cache
def get_compiled_graph():
    return build_graph().compile()
