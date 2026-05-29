from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.errors import install_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import install_middleware
from app.core.openapi import configure_openapi


def create_app() -> FastAPI:
    configure_logging(settings)
    log = get_logger(__name__)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version=settings.api_version,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs" if settings.enable_docs else None,
        redoc_url=f"{settings.api_prefix}/redoc" if settings.enable_docs else None,
    )

    configure_openapi(app)
    install_middleware(app, settings=settings)
    install_exception_handlers(app, debug=settings.debug)

    app.include_router(api_v1_router, prefix=settings.api_prefix)

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    log.info(
    "app_created | env=%s | debug=%s",
    settings.env,
    settings.debug)
    return app


app = create_app()

