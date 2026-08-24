from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActivityEvent(Base):
    __tablename__ = "activity_events"
    __table_args__ = (
        Index("ix_activity_events_user_created_at", "user_id", "created_at"),
        Index("ix_activity_events_type_created_at", "event_type", "created_at"),
        Index("ix_activity_events_movie_created_at", "movie_id", "created_at"),
        Index("ix_activity_events_user_type_created_at", "user_id", "event_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    movie_id: Mapped[object] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    event_metadata: Mapped[object] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="activity_events")
    movie = relationship("Movie", back_populates="activity_events")
