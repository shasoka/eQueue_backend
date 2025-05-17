import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket


__all__ = (
    "router",
    "manager",
)

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from core.config import settings
from core.exceptions import UnexpectedBroadcastException
from core.models import db_helper
from moodle.auth.oauth2 import MoodleOAuth2


class ConnectionManager:
    def __init__(self):
        # Активные соединения - словарь, где ключ - queue_id, значение -
        # список соединений (пользователей, просматривающих очередь)
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        queue_id: int,
    ):
        await websocket.accept()
        if queue_id not in self.active_connections:
            self.active_connections[queue_id] = []
        self.active_connections[queue_id].append(websocket)

    def disconnect(
        self,
        websocket: WebSocket,
        queue_id: int,
    ):
        self.active_connections[queue_id].remove(websocket)
        if not self.active_connections[queue_id]:
            del self.active_connections[queue_id]

    @staticmethod
    async def send_personal_message(
        message: str | dict,
        websocket: WebSocket,
    ):
        await websocket.send_text(
            json.dumps(
                message,
                ensure_ascii=False,
                default=str,
            )
        )

    async def broadcast(
        self,
        message: str,
        queue_id: int,
    ):
        if queue_id in self.active_connections:
            for connection in self.active_connections[queue_id]:
                await connection.send_text(
                    json.dumps(
                        message,
                        ensure_ascii=False,
                        default=str,
                    )
                )


manager = ConnectionManager()

router = APIRouter()


@router.websocket("/{queue_id}")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    queue_id: int,
    # Токен передается как query-параметр, т.к. в рамках обмена
    # сообщениями websocket не имеет заголовков
    token: Annotated[str, Query(...)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> None:

    # Получение текущего пользователя для проверки авторизации
    current_user = await MoodleOAuth2.validate_access_token(
        access_token=token,
        session=session,
    )

    # Подключение к вебсокету
    await manager.connect(
        websocket=websocket,
        queue_id=queue_id,
    )

    # Обмен сообщениями по websocket
    try:
        while True:
            pass
    except WebSocketDisconnect:
        manager.disconnect(
            websocket=websocket,
            queue_id=queue_id,
        )
    except Exception as e:
        manager.disconnect(
            websocket=websocket,
            queue_id=queue_id,
        )
        raise UnexpectedBroadcastException(
            f"Возникла проблема в работе websocket для очереди {queue_id}: {e}."
        )
