import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, structured_logging_middleware
from app.core.rate_limit import rate_limit_middleware
from app.db.base import init_db
from app.services.cache import reset_runtime_services

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    reset_runtime_services()
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    application = FastAPI(
        title=settings.app_name,
        summary="StreamSphere backend for content discovery, engagement, and AI-assisted recommendations.",
        description=settings.app_description,
        version=settings.api_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
        contact={"name": "StreamSphere", "url": "https://example.com/streamsphere"},
        license_info={"name": "MIT"},
        openapi_tags=[
            {"name": "health", "description": "Operational status and dependency monitoring."},
            {"name": "authentication", "description": "Registration and JWT login."},
            {"name": "movies", "description": "Catalog, ratings, summaries, and progress tracking."},
            {"name": "genres", "description": "Movie genre management."},
            {"name": "notifications", "description": "User notifications and real-time delivery."},
            {"name": "watchlist", "description": "User watchlist management."},
            {"name": "favorites", "description": "User favorites management."},
            {"name": "reviews", "description": "Review maintenance endpoints."},
            {"name": "recommendations", "description": "Personalized recommendation payloads."},
            {"name": "search", "description": "Natural-language movie discovery endpoints."},
            {"name": "home", "description": "Personalized home page aggregates."},
            {"name": "profile", "description": "Account details, profile views, and personal insights."},
            {"name": "admin", "description": "Administrative analytics, moderation, and AI maintenance."},
        ],
        servers=[
            {"url": "http://127.0.0.1:8000", "description": "Local development"},
            {"url": "http://localhost:8000", "description": "Docker Compose local stack"},
        ],
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.middleware("http")(structured_logging_middleware)
    application.middleware("http")(rate_limit_middleware)

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception while processing request", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    application.include_router(api_router)
    return application


app = create_app()
