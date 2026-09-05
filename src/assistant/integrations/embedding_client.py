"""Embedding client — API (Gemini/OpenAI-compatible) or deterministic mock for CI."""

from __future__ import annotations

import hashlib
import math
import struct

from assistant.core.config import settings

EMBED_DIM = 768


def _mock_vector(text: str) -> list[float]:
    """Deterministic unit-ish vector for tests without network."""
    seed = hashlib.sha256((text or " ").encode()).digest()
    raw = (seed * ((EMBED_DIM // len(seed)) + 1))[:EMBED_DIM]
    floats = [struct.unpack("B", bytes([b]))[0] / 255.0 for b in raw]
    norm = math.sqrt(sum(v * v for v in floats)) or 1.0
    return [v / norm for v in floats]


def _embed_api_batch(texts: list[str]) -> list[list[float]]:
    if not settings.openai_api_key.strip():
        raise RuntimeError(
            "OPENAI_API_KEY is empty. Set your provider key for EMBED_MODE=api."
        )
    try:
        from openai import OpenAI  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("Install 'openai' to use EMBED_MODE=api (uv sync)") from exc

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    batch_size = max(1, settings.embed_batch_size)
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = client.embeddings.create(
            model=settings.embed_model,
            input=batch,
        )
        vectors.extend(item.embedding for item in response.data)
    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if settings.embed_mode == "mock":
        return [_mock_vector(text) for text in texts]
    return _embed_api_batch(texts)


def embed_query(text: str) -> list[float]:
    return embed_documents([text or " "])[0]
