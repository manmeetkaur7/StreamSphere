from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    recommended_movie_ids: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_genres: Mapped[str] = mapped_column(Text, nullable=False)
    reason_for_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    user = relationship("User", back_populates="recommendation_cache")
