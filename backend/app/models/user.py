import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Uuid, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    watchlist_entries = relationship(
        "Watchlist",
        back_populates="user",
        passive_deletes=True,
    )
    favorite_entries = relationship(
        "Favorite",
        back_populates="user",
        passive_deletes=True,
    )
    ratings = relationship(
        "Rating",
        back_populates="user",
        passive_deletes=True,
    )
    reviews = relationship(
        "Review",
        back_populates="user",
        passive_deletes=True,
    )
