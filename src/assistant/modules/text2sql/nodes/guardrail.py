"""Two-layer intent guardrail — rules first so tests never need a real LLM."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from assistant.modules.text2sql.state import QueryState

_PROMPT_PATH = Path(__file__).resolve().parents[5] / "configs" / "prompts" / "text2sql.yaml"

_WRITE_RE = re.compile(
    r"\b(update|delete|insert|drop|truncate|alter)\b",
    re.IGNORECASE,
)


@lru_cache
def _load_guardrail_config() -> dict[str, Any]:
    if not _PROMPT_PATH.exists():
        return {}
    with _PROMPT_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("guardrail") or {}


def _contains_any(text: str, phrases: list[str]) -> str | None:
    for phrase in phrases:
        if phrase.lower() in text:
            return phrase
    return None


def check_intent(question: str) -> tuple[bool, str]:
    """Return ``(blocked, reason)``. Empty reason means allow."""
    q = question.lower().strip()
    cfg = _load_guardrail_config()

    if _WRITE_RE.search(q):
        return True, "Write/DDL intent is not allowed; only read queries."

    dump_hit = _contains_any(q, list(cfg.get("dump_keywords") or []))
    if dump_hit:
        return True, "Refusing a full-database dump; ask about a specific model."

    forbidden = list(cfg.get("forbidden_models") or [])
    hit = _contains_any(q, forbidden)
    if hit:
        return True, f"Model not allowed: {hit}"

    scope_hit = _contains_any(q, list(cfg.get("out_of_scope_keywords") or []))
    if scope_hit:
        return True, "Question is outside the mock ERP (orders, partners, products, stock)."

    return False, ""


def guardrail(state: QueryState) -> dict[str, Any]:
    blocked, reason = check_intent(state["question"])
    return {
        "blocked": blocked,
        "block_reason": reason,
        "tool_steps": 0,
        "models_used": [],
        "rows": [],
        "fetch_error": "",
    }
