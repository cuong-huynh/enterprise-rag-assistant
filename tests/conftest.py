"""Shared pytest fixtures."""

import pytest

from assistant.core import config


@pytest.fixture(autouse=True)
def _sync_ingest_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """CI and local tests ingest inline — no Redis required."""
    monkeypatch.setattr(config.settings, "ingest_mode", "sync")
    monkeypatch.setattr(config.settings, "redis_url", "")
