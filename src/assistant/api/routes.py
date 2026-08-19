import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from assistant.core.config import settings
from assistant.modules.rag import service as rag_service

router = APIRouter()


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    mode: str


class IngestResponse(BaseModel):
    file: str
    num_chunks: int


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest) -> AskResponse:
    result = await rag_service.ask(body.question)
    return AskResponse(answer=result.answer, sources=result.sources, mode=settings.llm_mode)


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile) -> IngestResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    result = await rag_service.ingest_file(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return IngestResponse(file=file.filename, num_chunks=result.num_chunks)
