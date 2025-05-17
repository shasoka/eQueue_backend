from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Queue
from core.schemas.queues import QueueCreate
from crud.subjects import check_foreign_key_subject_id
from crud.tasks import (
    check_if_user_is_permitted_to_get_tasks,
    check_if_user_is_permitted_to_modify_tasks,
)
from crud.workspace_members import check_if_user_is_workspace_member


# --- Ограничения уникальности ---


async def check_unique_subject_id(
    session: AsyncSession,
    subject_id: int,
) -> None:
    if await get_queue_by_subject_id(session, subject_id):
        raise UniqueConstraintViolationException(
            f"Нарушено ограничение уникальности в таблице queues: "
            f"значение {subject_id} уже существует в столбце subject_id."
        )


# --- Create ---


async def create_queue(
    session: AsyncSession,
    current_user_id: int,
    queue_in: QueueCreate,
) -> Queue:
    # Распаковка pydantic-модели в SQLAlchemy-модель
    queue: Queue = Queue(**queue_in.model_dump())

    # --- Ограничения уникальности ---

    # Проверка существования внешнего ключа subject_id
    await check_foreign_key_subject_id(
        session=session,
        subject_id=queue.subject_id,
    )

    # Проверка того, что пользователь является членом рабочего пространства, в
    # котором находится предмет
    # Используется данная фцнкция, т.к. она использует доступный из этой
    # области видимости subject_id
    await check_if_user_is_permitted_to_get_tasks(
        session=session,
        subject_id=queue.subject_id,
        user_id=current_user_id,
    )

    # Проверка уникальности subject_id
    await check_unique_subject_id(
        session=session,
        subject_id=queue.subject_id,
    )

    # ---

    session.add(queue)
    await session.commit()
    await session.refresh(queue)
    return queue


# --- Read ---


async def get_queue_by_subject_id(
    session: AsyncSession,
    subject_id: int,
    constraint_check: bool = True,
    check_admin: bool = False,
    user_id: Optional[int] = None,
) -> Optional[Queue]:
    stmt: Select = select(Queue).where(Queue.subject_id == subject_id)
    if queue := (await session.scalars(stmt)).one_or_none():
        if check_admin:
            # Используется данная фцнкция, т.к. она использует доступный из
            # этой области видимости subject_id
            await check_if_user_is_permitted_to_modify_tasks(
                session=session,
                subject_id=subject_id,
                user_id=user_id,
            )
        return queue
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(
            f"Очередь с subject_id={subject_id} не найдена."
        )
