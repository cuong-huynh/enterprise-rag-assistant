from fastapi import APIRouter

from assistant.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}
