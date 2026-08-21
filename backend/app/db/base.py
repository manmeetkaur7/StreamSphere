from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase

from app.db.database import engine


class Base(DeclarativeBase):
    pass


def register_models() -> None:
    from app.models.activity_event import ActivityEvent  # noqa: F401
    from app.models.favorite import Favorite  # noqa: F401
    from app.models.genre import Genre  # noqa: F401
    from app.models.movie import Movie  # noqa: F401
    from app.models.movie_genre import MovieGenre  # noqa: F401
    from app.models.movie_summary import MovieSummary  # noqa: F401
    from app.models.notification import Notification  # noqa: F401
    from app.models.rating import Rating  # noqa: F401
    from app.models.recommendation_cache import RecommendationCache  # noqa: F401
    from app.models.review import Review  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.watch_progress import WatchProgress  # noqa: F401
    from app.models.watchlist import Watchlist  # noqa: F401


def init_db() -> None:
    from app.services.content_seed import seed_content_data

    register_models()
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()
    seed_content_data()


def ensure_schema_compatibility() -> None:
    inspector = inspect(engine)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "is_admin" not in user_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
