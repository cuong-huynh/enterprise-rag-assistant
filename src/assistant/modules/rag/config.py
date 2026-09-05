"""Load RAG tuning from configs/rag.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

def repo_root() -> Path:
    """Repository root (enterprise-rag-assistant/)."""
    return Path(__file__).resolve().parents[4]


_RAG_CONFIG_PATH = repo_root() / "configs" / "rag.yaml"
_GENERATE_PROMPT_PATH = repo_root() / "configs" / "prompts" / "rag_generate.yaml"

_DEFAULTS = {
    "chunk_size": 800,
    "chunk_overlap": 150,
    "top_k": 5,
    "max_retrieve_steps": 3,
    "embed_batch_size": 32,
}


@lru_cache
def load_rag_config() -> dict[str, Any]:
    if not _RAG_CONFIG_PATH.exists():
        return dict(_DEFAULTS)
    with _RAG_CONFIG_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    merged = dict(_DEFAULTS)
    merged.update(data)
    return merged


@lru_cache
def load_generate_system_prompt() -> str:
    if not _GENERATE_PROMPT_PATH.exists():
        return ""
    with _GENERATE_PROMPT_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return str(data.get("system") or "").strip()
