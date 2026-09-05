from fastapi import APIRouter, HTTPException, UploadFile

from assistant.api.schemas import IngestResponse
from assistant.modules.ingest import service as ingest_service

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    result = await ingest_service.submit_pdf(file.filename, content)
    return IngestResponse(
        file=result.file,
        num_chunks=result.num_chunks,
        status=result.status,
        job_id=result.job_id,
    )
