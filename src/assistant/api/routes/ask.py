from fastapi import APIRouter

from assistant.api.schemas import AskRequest, AskResponse
from assistant.core.config import settings
from assistant.modules.rag import service as rag_service

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest) -> AskResponse:
    result = await rag_service.ask(body.question)
    return AskResponse(answer=result.answer, sources=result.sources, mode=settings.llm_mode)
