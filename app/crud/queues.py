"""Модуль, содержащий функции, реализующие CRUD-операции сущности Queue."""

from typing import Optional

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Queue, QueueMember
from core.schemas.queues import QueueCreate, QueueUpdate
from crud.subjects import check_foreign_key_subject_id
from crud.tasks import (
    check_if_user_is_permitted_to_get_tasks,
    check_if_user_is_permitted_to_modify_tasks,
)

__all__ = (
    "check_foreign_key_queue_id",
    "create_queue",
    "delete_queue",
    "get_queue_by_id",
    "get_queue_by_subject_id",
    "get_queue_for_ws_message",
    "update_queue",
)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_queue_id(
    session: AsyncSession,
    queue_id: int,
) -> None:
    """
    Функция, проверяющая существование внешнего ключа queue_id.

    Используется в CRUD-операциях других сущностей.

    :param session: сессия подключения к БД
    :param queue_id: id очереди в БД

    :raises ForeignKeyViolationException: если очередь с таким id не существует
    """

    if not await get_queue_by_id(session, queue_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа queue_id: "
            f"значение {queue_id} не существует в столбце id таблицы queues."
        )


# --- Ограничения уникальности ---


async def check_unique_subject_id(
    session: AsyncSession,
    subject_id: int,
) -> None:
    """
    Функция, проверяющая уникальность subject_id.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД

    :raises UniqueConstraintViolationException: если предмет с таким id
        уже существует
    """

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
    """
    Функция, реализующая создание очереди.

    :param session: сессия подключения к БД
    :param current_user_id: id текущего авторизованного пользователя
    :param queue_in: объект pydantic-модели QueueCreate
    :return: созданная очередь

    :raises ForeignKeyViolationException: если предмет с таким subject_id
        не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства, в котором находится очередь
    :raises UniqueConstraintViolationException: если предмет с таким subject_id
        уже существует
    """

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


async def get_queue_by_id(
    session: AsyncSession,
    queue_id: int,
) -> Optional[Queue]:
    """
    Функция, возвращающая очередь по id.

    :param session: сессия подключения к БД
    :param queue_id: id очереди в БД
    :return: очередь, если она существует, None в противном случае
    """

    return await session.get(Queue, queue_id)


async def get_queue_for_ws_message(
    session: AsyncSession,
    queue_id: int,
) -> list[dict]:
    """
    Функция, реализующая получение членов очереди для отправки по websocket.

    :param session: сессия подключения к БД
    :param queue_id: id очереди в БД
    :return: список членов очереди, приведенных к словарям
    """

    # Получение очереди с ее членами
    stmt: Select = (
        select(Queue)
        .where(Queue.id == queue_id)
        .options(selectinload(Queue.members).selectinload(QueueMember.user))
    )
    # Вернется гарантированно Queue, т.к. проверка существования такой очереди
    # происходит до вызова данной функции
    queue_with_members: Optional[Queue] = (
        await session.scalars(stmt)
    ).one_or_none()

    # Составление словаря с членами очереди для отправки по websocket
    result_set: list[dict] = []
    # noinspection PyTypeChecker
    sorted_members = sorted(
        queue_with_members.members, key=lambda memb: memb.position
    )
    for member in sorted_members:
        result_set.append(
            {
                "user_id": member.user_id,
                "queue_id": member.queue_id,
                "position": member.position,
                "status": member.status,
                "entered_at": member.entered_at,
                "first_name": member.user.first_name,
                "second_name": member.user.second_name,
                "profile_pic_url": member.user.profile_pic_url,
            }
        )

    return result_set


async def get_queue_by_subject_id(
    session: AsyncSession,
    subject_id: int,
    constraint_check: bool = True,
    check_admin: bool = False,
    check_membership: bool = False,
    user_id: Optional[int] = None,
) -> Optional[Queue]:
    """
    Функция, возвращающая очередь по subject_id.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param constraint_check: флаг, определяющий вернется ли None, или
        выбросится исключение
    :param check_admin: флаг, определяющий будет ли произведена проверка на
        права администратора пользователя
    :param check_membership: флаг, определяющий будет ли произведена проверка
        на принадлежность пользователя к рабочему пространству, в котором
        находится данная очередь
    :param user_id: id пользователя
    :return: очередь, если она существует, None в противном случае

    :raises NoEntityFoundException: если очередь с таким subject_id не
        существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства или администратором, в котором
        находится очередь
    """

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
        if check_membership:
            await check_if_user_is_permitted_to_get_tasks(
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


# --- Update ---


async def update_queue(
    session: AsyncSession,
    queue_upd: QueueUpdate,
    subject_id: int,
    user_id: int = None,
) -> Queue:
    """
    Функция, обновляющая объект очереди.

    :param session: сессия подключения к БД
    :param queue_upd: объект pydantic-модели QueueUpdate
    :param subject_id: id предмета в БД
    :param user_id: id пользователя в БД
    :return: обновленная очередь

    :raises ForeignKeyViolationException: если предмет с таким subject_id
        не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        очередь
    :raises NoEntityFoundException: если очередь с таким subject_id не
        существует
    """

    # Проверка существования внешнего ключа subject_id
    await check_foreign_key_subject_id(
        session=session,
        subject_id=subject_id,
    )

    # Получение очереди по subject_id
    # Тут же проверка является ли пользователь администратором для обновления
    # очереди
    queue: Queue = await get_queue_by_subject_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
        check_admin=True,
        user_id=user_id,
    )

    # Распаковка pydantic-модели в SQLAlchemy-модель
    queue_upd: dict = queue_upd.model_dump(exclude_unset=True)

    for key, value in queue_upd.items():
        setattr(queue, key, value)

    await session.commit()
    await session.refresh(queue)
    return queue


# --- Delete ---


async def delete_queue(
    session: AsyncSession,
    subject_id: int,
    user_id: int = None,
) -> Queue:
    """
    Функция, удаляющая объект очереди.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param user_id: id пользователя в БД
    :return: удаленная очередь

    :raises ForeignKeyViolationException: если предмет с таким subject_id
        не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        очередь
    :raises NoEntityFoundException: если очередь с таким subject_id не
        существует
    """

    # Проверка существования внешнего ключа subject_id
    await check_foreign_key_subject_id(
        session=session,
        subject_id=subject_id,
    )

    # Получение очереди по subject_id
    # Тут же происходит проверка является ли пользователь администратором для
    # удаления очереди
    queue: Queue = await get_queue_by_subject_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
        check_admin=True,
        user_id=user_id,
    )

    await session.delete(queue)
    await session.commit()
    return queue
