"""Application factory — composition only, no business logic here."""

from fastapi import FastAPI, Request

from assistant.api.routes import ask, chat, health, ingest, query
from assistant.core.config import settings
from assistant.core.logging import REQUEST_ID_HEADER, configure_logging, set_request_id


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request_id = set_request_id(request.headers.get(REQUEST_ID_HEADER))
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

    app.include_router(chat.router)
    app.include_router(health.router)
    app.include_router(ask.router)
    app.include_router(ingest.router)
    app.include_router(query.router)
    return app


app = create_app()
