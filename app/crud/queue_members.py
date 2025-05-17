from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.queue_websocket import manager
from core.exceptions import UniqueConstraintViolationException
from core.models import Queue, QueueMember
from crud.queues import check_foreign_key_queue_id, get_queue_by_id
from crud.tasks import check_if_user_is_permitted_to_get_tasks


# --- Ограничения уникальности ---


async def check_complex_unique_user_id_queue_id(
    session: AsyncSession,
    user_id: int,
    queue_id: int,
) -> None:
    if await get_queue_member_by_user_id_and_queue_id(
        session=session,
        user_id=user_id,
        queue_id=queue_id,
    ):
        raise UniqueConstraintViolationException(
            f"Нарушено ограничение уникальности user_id и queue_id: пара "
            f"значений {user_id} и {queue_id} уже существует в таблице "
            f"queue_members."
        )


# --- Create ---


async def _get_next_position_in_queue_by_queue_id(
    session: AsyncSession,
    queue_id: int,
) -> int:
    stmt: Select = (
        select(QueueMember.position)
        .where(QueueMember.queue_id == queue_id)
        .order_by(QueueMember.position.desc())
    )

    last_position: Optional[int] = (await session.scalars(stmt)).one_or_none()

    return 0 if last_position is None else last_position + 1


async def create_queue_member(
    session: AsyncSession,
    current_user_id: int,
    queue_id: int,
) -> QueueMember:
    # --- Ограничения уникальности ---

    # Проверка существования внешнего ключа queue_id
    await check_foreign_key_queue_id(
        session=session,
        queue_id=queue_id,
    )

    # Проврека членства пользователя в рабочем пространстве, в котором
    # находится очередь
    queue: Queue = await get_queue_by_id(
        session=session,
        queue_id=queue_id,
    )
    await check_if_user_is_permitted_to_get_tasks(
        session=session,
        subject_id=queue.subject_id,
        user_id=current_user_id,
    )

    # Проверка составного ограничения уникальности user_id и queue_id
    await check_complex_unique_user_id_queue_id(
        session=session,
        user_id=current_user_id,
        queue_id=queue_id,
    )

    # ---

    queue_member: QueueMember = QueueMember(
        user_id=current_user_id,
        queue_id=queue_id,
        position=await _get_next_position_in_queue_by_queue_id(
            session=session,
            queue_id=queue_id,
        ),
        status="active",
    )

    session.add(queue_member)
    await session.commit()
    await session.refresh(queue_member)

    # Оповещение подписчиков о новом состоянии очереди
    await manager.notify_subs_about_queue_update(
        session=session,
        queue_id=queue_id,
    )

    return queue_member


# --- Read ---


async def get_queue_member_by_user_id_and_queue_id(
    session: AsyncSession,
    user_id: int,
    queue_id: int,
) -> Optional[QueueMember]:
    stmt: Select = select(QueueMember).where(
        QueueMember.user_id == user_id,
        QueueMember.queue_id == queue_id,
    )

    return (await session.scalars(stmt)).one_or_none()
