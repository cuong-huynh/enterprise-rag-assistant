"""Application factory — composition only, no business logic here."""

from fastapi import FastAPI

from assistant.api.routes import ask, health, ingest, query
from assistant.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
    app.include_router(health.router)
    app.include_router(ask.router)
    app.include_router(ingest.router)
    app.include_router(query.router)
    return app


app = create_app()
