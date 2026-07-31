from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    poster_url: Mapped[str] = mapped_column(String(500), nullable=False)
    trailer_url: Mapped[str] = mapped_column(String(500), nullable=False)
    maturity_rating: Mapped[str] = mapped_column(String(16), nullable=False)
    language: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    genres = relationship(
        "Genre",
        secondary="movie_genres",
        back_populates="movies",
        passive_deletes=True,
    )
    watchlist_entries = relationship(
        "Watchlist",
        back_populates="movie",
        passive_deletes=True,
    )
    favorite_entries = relationship(
        "Favorite",
        back_populates="movie",
        passive_deletes=True,
    )
    ratings = relationship(
        "Rating",
        back_populates="movie",
        passive_deletes=True,
    )
    reviews = relationship(
        "Review",
        back_populates="movie",
        passive_deletes=True,
    )
