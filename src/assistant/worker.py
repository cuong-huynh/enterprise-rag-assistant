"""Ingest worker — dequeue PDF jobs from Redis and embed into Chroma."""

from __future__ import annotations

import asyncio
import signal
from pathlib import Path

from assistant.core.config import settings
from assistant.core.logging import configure_logging, get_logger, set_request_id
from assistant.integrations.ingest_queue import dequeue_blocking
from assistant.modules.rag import service as rag_service

logger = get_logger(__name__)
_stop = False


def _handle_stop(*_args: object) -> None:
    global _stop
    _stop = True
    logger.info("Worker shutdown requested")


async def _process_job(path: str, display_name: str) -> int:
    file_path = Path(path)
    try:
        result = await rag_service.ingest_file(file_path, display_name=display_name)
        logger.info("Ingested %s (%d chunks)", result.file, result.num_chunks)
        return result.num_chunks
    finally:
        file_path.unlink(missing_ok=True)


async def run_once() -> bool:
    """Process one queued job if available. Returns False when idle."""
    job = await asyncio.to_thread(dequeue_blocking, 5)
    if job is None:
        return False
    set_request_id(job.job_id)
    await _process_job(job.path, job.display_name)
    return True


async def run_forever() -> None:
    logger.info(
        "Ingest worker started (redis=%s, chroma=%s)",
        settings.redis_url or "(unset)",
        settings.chroma_persist_dir,
    )
    while not _stop:
        try:
            processed = await run_once()
        except Exception:
            logger.exception("Worker loop error; retrying")
            await asyncio.sleep(1)
            continue
        if not processed:
            await asyncio.sleep(0.1)


def main() -> None:
    configure_logging()
    if settings.ingest_mode != "queue" or not settings.redis_url.strip():
        raise SystemExit("Worker requires INGEST_MODE=queue and REDIS_URL.")
    signal.signal(signal.SIGINT, _handle_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_stop)
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
