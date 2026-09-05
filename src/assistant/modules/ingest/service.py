"""Submit PDFs for indexing — inline (sync) or via Redis queue."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from assistant.core.config import settings
from assistant.integrations.ingest_queue import IngestJob, enqueue, new_job_id, queue_enabled
from assistant.modules.rag import service as rag_service


@dataclass(frozen=True)
class IngestSubmission:
    file: str
    num_chunks: int
    status: str  # "completed" | "queued"
    job_id: str | None = None


def _inbox_path(job_id: str, filename: str) -> Path:
    settings.ingest_inbox_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name
    return settings.ingest_inbox_dir / f"{job_id}_{safe_name}"


async def submit_pdf(filename: str, content: bytes) -> IngestSubmission:
    """Ingest immediately or enqueue for the worker, depending on settings."""
    if queue_enabled():
        job_id = new_job_id()
        dest = _inbox_path(job_id, filename)
        dest.write_bytes(content)
        enqueue(IngestJob(job_id=job_id, path=str(dest), display_name=filename))
        return IngestSubmission(
            file=filename,
            num_chunks=0,
            status="queued",
            job_id=job_id,
        )

    # sync path (CI, local dev without Redis)
    tmp_path = settings.ingest_inbox_dir / f"sync_{uuid.uuid4().hex}_{Path(filename).name}"
    settings.ingest_inbox_dir.mkdir(parents=True, exist_ok=True)
    tmp_path.write_bytes(content)
    try:
        result = await rag_service.ingest_file(tmp_path, display_name=filename)
    finally:
        tmp_path.unlink(missing_ok=True)
    return IngestSubmission(
        file=result.file,
        num_chunks=result.num_chunks,
        status="completed",
        job_id=None,
    )
