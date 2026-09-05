"""Structured logging helpers."""

from __future__ import annotations

import contextvars
import logging
import uuid
from typing import Final

REQUEST_ID_HEADER: Final = "X-Request-ID"

_request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging once per process."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] request_id=%(request_id)s %(message)s",
    )
    _RequestIdFilter.install()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_request_id(request_id: str | None = None) -> str:
    value = (request_id or "").strip() or str(uuid.uuid4())
    _request_id.set(value)
    return value


def get_request_id() -> str:
    return _request_id.get()


class _RequestIdFilter(logging.Filter):
    """Inject ``request_id`` into every log record."""

    @classmethod
    def install(cls) -> None:
        filt = cls()
        root = logging.getLogger()
        for handler in root.handlers:
            handler.addFilter(filt)

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()  # type: ignore[attr-defined]
        return True
