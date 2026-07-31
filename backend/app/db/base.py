from sqlalchemy.orm import DeclarativeBase

from app.db.database import engine


class Base(DeclarativeBase):
    pass


def register_models() -> None:
    from app.models.favorite import Favorite  # noqa: F401
    from app.models.genre import Genre  # noqa: F401
    from app.models.movie import Movie  # noqa: F401
    from app.models.movie_genre import MovieGenre  # noqa: F401
    from app.models.rating import Rating  # noqa: F401
    from app.models.review import Review  # noqa: F401
    from app.models.user import User  # noqa: F401
    from app.models.watchlist import Watchlist  # noqa: F401


def init_db() -> None:
    from app.services.content_seed import seed_content_data

    register_models()
    Base.metadata.create_all(bind=engine)
    seed_content_data()
