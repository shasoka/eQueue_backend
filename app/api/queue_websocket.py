import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from core.exceptions import UnexpectedWebsocketException
from core.models import db_helper, Queue
from crud.queues import (
    check_foreign_key_queue_id,
    get_queue_by_id,
    get_queue_for_ws_message,
)
from crud.tasks import check_if_user_is_permitted_to_get_tasks
from moodle.auth.oauth2 import MoodleOAuth2

__all__ = (
    "router",
    "manager",
)


class ConnectionManager:
    def __init__(self) -> None:
        # Активные соединения - словарь, где ключ - queue_id, значение -
        # список соединений (пользователей, просматривающих очередь)
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        queue_id: int,
    ) -> None:
        await websocket.accept()
        if queue_id not in self.active_connections:
            self.active_connections[queue_id] = []
        self.active_connections[queue_id].append(websocket)

    def disconnect(
        self,
        websocket: WebSocket,
        queue_id: int,
    ) -> None:
        self.active_connections[queue_id].remove(websocket)
        if not self.active_connections[queue_id]:
            del self.active_connections[queue_id]

    @staticmethod
    async def send_personal_message(
        message: str | dict | list,
        websocket: WebSocket,
    ) -> None:
        await websocket.send_text(
            json.dumps(
                message,
                ensure_ascii=False,
                default=str,
            )
        )

    async def broadcast(
        self,
        message: str | dict | list,
        queue_id: int,
    ) -> None:
        if queue_id in self.active_connections:
            for connection in self.active_connections[queue_id]:
                await connection.send_text(
                    json.dumps(
                        message,
                        ensure_ascii=False,
                        default=str,
                    )
                )

    async def notify_subs_about_queue_update(
        self,
        session: AsyncSession,
        queue_id: int,
    ) -> None:
        # Получение нового состояния очереди
        updated_queue: list[dict] = await get_queue_for_ws_message(
            session=session,
            queue_id=queue_id,
        )

        # Отправка нового состояния всем активным подписчикам
        await self.broadcast(
            message=updated_queue,
            queue_id=queue_id,
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

    # Проверка существования внешнего ключа queue_id
    await check_foreign_key_queue_id(
        session=session,
        queue_id=queue_id,
    )

    # Проверка является ли пользователь, подключающийся к очереди, членом
    # рабочего пространства, в котором находится данная очередь
    queue: Queue = await get_queue_by_id(
        session=session,
        queue_id=queue_id,
    )
    await check_if_user_is_permitted_to_get_tasks(
        session=session,
        subject_id=queue.subject_id,
        user_id=current_user.id,  # type: ignore
    )

    # Подключение к вебсокету
    await manager.connect(
        websocket=websocket,
        queue_id=queue_id,
    )

    # Обмен сообщениями по websocket
    try:
        while True:
            # Получение сообщения
            data = await websocket.receive_text()

            # Обработка сообщения и возврат ответа
            if data == "get_queue":
                casted_queue: list[dict] = await get_queue_for_ws_message(
                    session=session,
                    queue_id=queue_id,
                )
                await manager.send_personal_message(
                    message=casted_queue,
                    websocket=websocket,
                )
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
        raise UnexpectedWebsocketException(
            f"Произошла ошибка вебсокета с queue_id={queue_id}: {e}"
        )
