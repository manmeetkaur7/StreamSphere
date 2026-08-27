from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ROOT_ENV_FILE)
load_dotenv(BACKEND_ENV_FILE, override=True)


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.app_name = "StreamSphere API"
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        self.app_environment = os.getenv("APP_ENV", "development").strip().lower()
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        self.app_description = (
            "StreamSphere is a FastAPI backend for catalog browsing, engagement features, "
            "and AI-assisted discovery across movies, watchlists, reviews, recommendations, and search."
        )
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/streamsphere")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        self.db_pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.db_max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.db_pool_timeout_seconds = int(os.getenv("DB_POOL_TIMEOUT_SECONDS", "30"))
        self.cache_default_ttl_seconds = int(os.getenv("CACHE_DEFAULT_TTL_SECONDS", "300"))
        self.recommendation_cache_ttl_seconds = int(
            os.getenv("RECOMMENDATION_CACHE_TTL_SECONDS", "300")
        )
        self.ai_search_cache_ttl_seconds = int(os.getenv("AI_SEARCH_CACHE_TTL_SECONDS", "600"))
        self.movie_summary_cache_ttl_seconds = int(
            os.getenv("MOVIE_SUMMARY_CACHE_TTL_SECONDS", "3600")
        )
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.ai_provider_name = os.getenv("AI_PROVIDER", "mock").strip().lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ai_request_timeout_seconds = float(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "3"))
        self.ai_request_retries = int(os.getenv("AI_REQUEST_RETRIES", "1"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.docs_enabled = os.getenv("DOCS_ENABLED", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.structured_logging_enabled = (
            os.getenv("STRUCTURED_LOGGING_ENABLED", "true").lower() == "true"
        )
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.security_headers_enabled = (
            os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        )
        self.content_security_policy = os.getenv(
            "CONTENT_SECURITY_POLICY",
            "default-src 'self'; img-src 'self' https: data:; media-src 'self' https:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "connect-src 'self' http: https: ws: wss:;",
        )
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
        self.rate_limit_window_seconds = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
        self.rate_limit_exempt_paths = tuple(
            path.strip()
            for path in os.getenv(
                "RATE_LIMIT_EXEMPT_PATHS",
                "/health,/metrics,/docs,/redoc,/openapi.json",
            ).split(",")
            if path.strip()
        )
        self.origins_explicitly_configured = bool(os.getenv("ALLOWED_ORIGINS", "").strip())
        configured_origins = [
            origin.strip()
            for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ]
        local_dev_origins = [
            f"http://localhost:{port}"
            for port in (3000, 3001, 3002)
        ] + [
            f"http://127.0.0.1:{port}"
            for port in (3000, 3001, 3002)
        ]
        self.allowed_origins = tuple(
            dict.fromkeys(
                configured_origins
                if self.app_environment == "production"
                else [*configured_origins, *local_dev_origins]
            )
        )
        self._validate_production_settings()

    def _validate_production_settings(self) -> None:
        if self.app_environment != "production":
            return

        errors: list[str] = []
        if not self.database_url or "postgres:password@" in self.database_url:
            errors.append("DATABASE_URL must be configured with production credentials.")
        if not self.jwt_secret_key or self.jwt_secret_key == "change-this-secret-in-production":
            errors.append("JWT_SECRET_KEY must be set to a strong, non-default value.")
        if not self.origins_explicitly_configured or not self.allowed_origins or "*" in self.allowed_origins:
            errors.append("ALLOWED_ORIGINS must list explicit frontend origins.")
        if self.ai_provider_name == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when AI_PROVIDER=openai.")

        if errors:
            raise RuntimeError("Invalid production configuration: " + " ".join(errors))


@lru_cache
def get_settings() -> Settings:
    return Settings()
