from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent

SENSITIVE_KEYS = {"password", "token", "jwt", "authorization", "api_key", "secret"}


def _sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                continue
            sanitized[key] = _sanitize_metadata(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def record_activity(
    db: Session,
    *,
    user_id: UUID,
    event_type: str,
    movie_id: int | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = False,
) -> ActivityEvent:
    event = ActivityEvent(
        user_id=user_id,
        event_type=event_type,
        movie_id=movie_id,
        event_metadata=_sanitize_metadata(metadata),
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    else:
        db.flush()
    return event


def count_activity_events(db: Session, event_type: str) -> int:
    return int(db.scalar(select(func.count(ActivityEvent.id)).where(ActivityEvent.event_type == event_type)) or 0)
