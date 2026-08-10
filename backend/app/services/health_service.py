from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.cache import get_cache_service

STARTED_AT = datetime.now(timezone.utc)


def uptime_seconds() -> int:
    return int((datetime.now(timezone.utc) - STARTED_AT).total_seconds())


def database_health(db: Session) -> tuple[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return "ok", "Database connection succeeded."
    except SQLAlchemyError as exc:
        return "unavailable", f"Database connection failed: {exc.__class__.__name__}."


def redis_health() -> tuple[str, str, str]:
    cache_service = get_cache_service()
    available, backend_name = cache_service.ping()
    if available and backend_name == "redis":
        return "ok", backend_name, "Redis cache is available."
    if available:
        return "degraded", backend_name, "Redis is disabled; using in-memory cache."
    return "degraded", backend_name, "Redis unavailable; using in-memory cache fallback."


def application_health(db: Session) -> dict[str, object]:
    settings = get_settings()
    database_status, database_detail = database_health(db)
    redis_status, redis_backend, redis_detail = redis_health()
    overall_status = "ok" if database_status == "ok" and redis_status == "ok" else "degraded"
    if database_status != "ok":
        overall_status = "unavailable"

    return {
        "status": overall_status,
        "environment": settings.app_environment,
        "version": settings.api_version,
        "uptime_seconds": uptime_seconds(),
        "database": {
            "status": database_status,
            "backend": "postgresql",
            "detail": database_detail,
        },
        "redis": {
            "status": redis_status,
            "backend": redis_backend,
            "detail": redis_detail,
        },
    }
