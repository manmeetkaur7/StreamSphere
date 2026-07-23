from functools import lru_cache
import os


class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = "StreamSphere API"
    api_version: str = "v1"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
