from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import WebSocket

from app.services.metrics import get_metrics_registry


class NotificationConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[user_id].add(websocket)
        get_metrics_registry().increment("websocket.notifications.connections")

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        get_metrics_registry().increment("websocket.notifications.disconnections")
        if not sockets:
            self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: UUID, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for websocket in list(self._connections.get(user_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:
                stale.append(websocket)

        for websocket in stale:
            self.disconnect(user_id, websocket)


notification_connection_manager = NotificationConnectionManager()
