from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)


class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = "StreamSphere API"
    api_version: str = "v1"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/streamsphere",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
