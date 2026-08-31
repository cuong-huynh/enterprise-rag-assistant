"""Rule-based route classifier — mock-safe for CI; LLM stretch after golden is green."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml

Route = Literal["rag", "data", "hybrid"]

_PROMPT_PATH = Path(__file__).resolve().parents[4] / "configs" / "prompts" / "dispatcher.yaml"


@dataclass(frozen=True)
class RouteDecision:
    route: Route
    reason: str
    data_hits: tuple[str, ...] = ()
    rag_hits: tuple[str, ...] = ()


@lru_cache
def _load_config() -> dict[str, Any]:
    if not _PROMPT_PATH.exists():
        return {}
    with _PROMPT_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _find_hits(text: str, phrases: list[str]) -> list[str]:
    hits: list[str] = []
    for phrase in phrases:
        if phrase.lower() in text:
            hits.append(phrase)
    return hits


def classify_route(question: str) -> RouteDecision:
    """Return rag, data, or hybrid with a short reason string."""
    q = question.lower().strip()
    cfg = _load_config()

    hybrid_hits = _find_hits(q, list(cfg.get("hybrid_keywords") or []))
    if hybrid_hits:
        return RouteDecision(
            route="hybrid",
            reason=f"Hybrid intent ({hybrid_hits[0]}).",
            data_hits=tuple(hybrid_hits),
        )

    data_hits = _find_hits(q, list(cfg.get("data_keywords") or []))
    rag_hits = _find_hits(q, list(cfg.get("rag_keywords") or []))

    if data_hits and rag_hits:
        return RouteDecision(
            route="hybrid",
            reason=f"Document + data signals ({rag_hits[0]} + {data_hits[0]}).",
            data_hits=tuple(data_hits),
            rag_hits=tuple(rag_hits),
        )
    if data_hits:
        return RouteDecision(
            route="data",
            reason=f"Structured ERP query ({data_hits[0]}).",
            data_hits=tuple(data_hits),
        )
    if rag_hits:
        return RouteDecision(
            route="rag",
            reason=f"Document / procedure question ({rag_hits[0]}).",
            rag_hits=tuple(rag_hits),
        )

    return RouteDecision(
        route="rag",
        reason="No strong routing signal; defaulting to document search.",
    )
