from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from assistant.api.schemas import ChatRequest, ChatResponse
from assistant.modules.dispatcher import service as dispatcher_service

router = APIRouter(tags=["chat"])

_STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
_CHAT_HTML = _STATIC_DIR / "chat.html"


@router.get("/")
async def chat_page() -> FileResponse:
    return FileResponse(_CHAT_HTML, media_type="text/html")


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    result = await dispatcher_service.chat(body.question)
    return ChatResponse(
        answer=result.answer,
        route=result.route,
        reason=result.reason,
        sources=result.sources,
        blocked=result.blocked,
        block_reason=result.block_reason,
        models_used=result.models_used,
        tool_steps=result.tool_steps,
    )
