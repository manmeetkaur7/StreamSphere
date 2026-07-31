from sqlalchemy.orm import DeclarativeBase

from app.db.database import engine


class Base(DeclarativeBase):
    pass


def register_models() -> None:
    from app.models.user import User  # noqa: F401


def init_db() -> None:
    register_models()
    Base.metadata.create_all(bind=engine)
