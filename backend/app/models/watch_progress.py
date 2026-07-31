from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WatchProgress(Base):
    __tablename__ = "watch_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_watch_progress_user_movie"),
        Index("ix_watch_progress_user_last_watched", "user_id", "last_watched"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    progress_percentage: Mapped[int] = mapped_column(nullable=False)
    last_watched: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    completed: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="false")

    user = relationship("User", back_populates="watch_progress_entries")
    movie = relationship("Movie", back_populates="progress_entries")
