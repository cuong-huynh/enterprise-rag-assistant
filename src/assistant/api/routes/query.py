from fastapi import APIRouter

from assistant.api.schemas import QueryRequest, QueryResponse
from assistant.modules.text2sql import service as text2sql_service

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    result = await text2sql_service.ask(body.question)
    return QueryResponse(
        answer=result.answer,
        blocked=result.blocked,
        block_reason=result.block_reason,
        models_used=result.models_used,
        tool_steps=result.tool_steps,
    )
