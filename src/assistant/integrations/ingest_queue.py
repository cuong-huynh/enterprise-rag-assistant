"""Redis-backed ingest job queue (P5).

API enqueues PDF paths; the worker dequeues and calls ``rag.service.ingest_file``.
When ``INGEST_MODE=sync`` (default), the API ingests inline — used in CI and local dev.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from assistant.core.config import settings
from assistant.core.logging import get_logger

logger = get_logger(__name__)

QUEUE_KEY = "ingest:jobs"


@dataclass(frozen=True)
class IngestJob:
    job_id: str
    path: str
    display_name: str

    @classmethod
    def from_json(cls, raw: str) -> IngestJob:
        data: dict[str, Any] = json.loads(raw)
        return cls(
            job_id=str(data["job_id"]),
            path=str(data["path"]),
            display_name=str(data["display_name"]),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def new_job_id() -> str:
    return str(uuid.uuid4())


def queue_enabled() -> bool:
    return settings.ingest_mode == "queue" and bool(settings.redis_url.strip())


def _client():
    import redis  # noqa: PLC0415

    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(job: IngestJob) -> None:
    if not queue_enabled():
        raise RuntimeError("Ingest queue is not enabled (INGEST_MODE=queue + REDIS_URL).")
    client = _client()
    client.lpush(QUEUE_KEY, job.to_json())
    logger.info("Enqueued ingest job %s for %s", job.job_id, job.display_name)


def dequeue_blocking(timeout_seconds: int = 5) -> IngestJob | None:
    if not settings.redis_url.strip():
        return None
    import redis  # noqa: PLC0415

    client = _client()
    try:
        item = client.brpop(QUEUE_KEY, timeout=timeout_seconds)
    except redis.TimeoutError:
        # redis-py 8: idle BRPOP raises Redis TimeoutError (not builtins.TimeoutError)
        return None
    if item is None:
        return None
    _key, payload = item
    job = IngestJob.from_json(payload)
    logger.info("Dequeued ingest job %s", job.job_id)
    return job
