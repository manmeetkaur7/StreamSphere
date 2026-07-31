from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MovieSummary(Base):
    __tablename__ = "movie_summaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    short_summary: Mapped[str] = mapped_column(Text, nullable=False)
    long_summary: Mapped[str] = mapped_column(Text, nullable=False)
    main_themes: Mapped[str] = mapped_column(Text, nullable=False)
    viewer_type: Mapped[str] = mapped_column(Text, nullable=False)
    provider_name: Mapped[str] = mapped_column(nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
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

    movie = relationship("Movie", back_populates="summaries")
