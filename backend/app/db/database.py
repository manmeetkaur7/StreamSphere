from sqlalchemy import create_engine

from app.core.config import get_settings

settings = get_settings()
database_url = settings.database_url

if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)
