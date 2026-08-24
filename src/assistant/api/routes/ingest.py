import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from assistant.api.schemas import IngestResponse
from assistant.modules.rag import service as rag_service

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    result = await rag_service.ingest_file(tmp_path, display_name=file.filename)
    tmp_path.unlink(missing_ok=True)
    return IngestResponse(file=file.filename, num_chunks=result.num_chunks)
