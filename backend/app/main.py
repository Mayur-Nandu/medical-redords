from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.middleware.security import SecurityHeadersMiddleware
from app.db.session import Base, engine


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    logger = get_logger()

    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        default_response_class=ORJSONResponse,
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Root ping - non-sensitive
    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"message": "Medical History API"}

    # API v1 routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info("Application initialized")
    return app


Base.metadata.create_all(bind=engine)
app = create_app()

