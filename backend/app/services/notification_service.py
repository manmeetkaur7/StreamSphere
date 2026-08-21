from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.platform import NotificationEventResponse, NotificationResponse
from app.services.notification_realtime import notification_connection_manager


def list_notifications(db: Session, user_id: UUID) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
        ).all()
    )


def unread_notification_count(db: Session, user_id: UUID) -> int:
    return int(
        db.scalar(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        or 0
    )


async def push_notification_event(db: Session, notification: Notification, event: str = "notification.created") -> None:
    unread_count = unread_notification_count(db, notification.user_id)
    payload = NotificationEventResponse(
        event=event,
        notification=NotificationResponse.model_validate(notification),
        unread_count=unread_count,
    )
    await notification_connection_manager.send_to_user(notification.user_id, payload.model_dump(mode="json"))


async def create_notification(
    db: Session,
    *,
    user_id: UUID,
    notification_type: str,
    title: str,
    message: str,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    await push_notification_event(db, notification)
    return notification


async def mark_notification_read(db: Session, *, notification: Notification) -> Notification:
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    await push_notification_event(db, notification, event="notification.updated")
    return notification


async def mark_notifications_read(db: Session, notifications: Iterable[Notification]) -> int:
    updated = 0
    touched: list[Notification] = []
    for notification in notifications:
        if notification.is_read:
            continue
        notification.is_read = True
        touched.append(notification)
        updated += 1
    if not updated:
        return 0
    db.commit()
    for notification in touched:
        db.refresh(notification)
        await push_notification_event(db, notification, event="notification.updated")
    return updated
