from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_user_from_token
from app.db.session import SessionLocal, get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.platform import NotificationResponse, NotificationUnreadCountResponse
from app.services.notification_realtime import notification_connection_manager
from app.services.notification_service import (
    list_notifications,
    mark_notification_read,
    mark_notifications_read,
    unread_notification_count,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])
websocket_router = APIRouter(tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    return [NotificationResponse.model_validate(item) for item in list_notifications(db, current_user.id)]


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationUnreadCountResponse:
    return NotificationUnreadCountResponse(unread_count=unread_notification_count(db, current_user.id))


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return NotificationResponse.model_validate(await mark_notification_read(db, notification=notification))


@router.put("/read-all", response_model=NotificationUnreadCountResponse)
async def read_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationUnreadCountResponse:
    notifications = list_notifications(db, current_user.id)
    await mark_notifications_read(db, notifications)
    return NotificationUnreadCountResponse(unread_count=unread_notification_count(db, current_user.id))


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    db.delete(notification)
    db.commit()


@websocket_router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    bearer = websocket.headers.get("authorization", "")
    if token is None and bearer.lower().startswith("bearer "):
        token = bearer[7:]
    if not token:
        await websocket.close(code=1008, reason="Authentication required.")
        return

    with SessionLocal() as db:
        try:
            user = get_user_from_token(token, db)
        except HTTPException:
            await websocket.close(code=1008, reason="Invalid credentials.")
            return

    await notification_connection_manager.connect(user.id, websocket)
    try:
        with SessionLocal() as db:
            unread_count = unread_notification_count(db, user.id)
        await websocket.send_json(
            {
                "event": "notifications.ready",
                "unread_count": unread_count,
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()
    finally:
        notification_connection_manager.disconnect(user.id, websocket)
