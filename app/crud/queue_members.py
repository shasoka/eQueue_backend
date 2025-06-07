"""Модуль, содержащий функции, реализующие CRUD-операции сущности QueueMember."""

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api.queue_websocket import manager
from core.exceptions import (
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Queue, QueueMember, Task
from crud.queues import check_foreign_key_queue_id, get_queue_by_id
from crud.submissions import (
    create_submission,
    get_submission_by_user_id_and_task_id,
)
from crud.tasks import (
    check_if_user_is_permitted_to_get_tasks,
    get_tasks_by_subject_id,
)

__all__ = (
    "create_queue_member",
    "get_queue_member_by_user_id_and_queue_id",
    "leave_queue_by_user_id_and_queue_id",
    "switch_queue_member_status_by_user_id_and_queue_id",
)


# --- Комплексная проверка, использующаяся во многих функциях ---


async def complex_queue_member_check(
    session: AsyncSession,
    current_user_id: int,
    queue_id: int,
) -> QueueMember:
    """
    Функция, реализующая комплексную проверку доступа к члену очереди.

    Используется в функциях ниже.

    :param session: сессия подключения к БД
    :param current_user_id: id текущего авторизованного пользователя
    :param queue_id: id очереди
    :return: член очереди

    :raises ForeignKeyViolationException: если очередь с таким id не существует
    :raises NoEntityFoundException: если член очереди с таким current_user_id
        и queue_id не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства, в котором находится очередь
    """

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

    # Получение члена очереди
    queue_member: QueueMember = await get_queue_member_by_user_id_and_queue_id(
        session=session,
        user_id=current_user_id,
        queue_id=queue_id,
    )

    return queue_member


# --- Ограничения уникальности ---


async def check_complex_unique_user_id_queue_id(
    session: AsyncSession,
    user_id: int,
    queue_id: int,
) -> None:
    """
    Функция, выполняющая проверку уникальности пары значений user_id и
    queue_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя
    :param queue_id: id очереди

    :raises UniqueConstraintViolationException: если пара значений user_id и
        queue_id не уникальна
    """

    if await get_queue_member_by_user_id_and_queue_id(
        session=session,
        user_id=user_id,
        queue_id=queue_id,
        constraint_check=True,
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
    """
    Функция, вычисляющая следующее значение поля position в очереди.

    :param session: сессия подключения к БД
    :param queue_id: id очереди
    :return: следующее значение поля position
    """

    stmt: Select = (
        select(QueueMember.position)
        .where(QueueMember.queue_id == queue_id)
        .order_by(QueueMember.position.desc())
    )

    last_position: Optional[int] = (await session.scalars(stmt)).first()

    return 0 if last_position is None else last_position + 1


async def create_queue_member(
    session: AsyncSession,
    current_user_id: int,
    queue_id: int,
) -> QueueMember:
    """
    Функция, реализующая создание члена очереди.

    После создания оповещает все активные вебсокеты об изменении очереди.

    :param session: сессия подключения к БД
    :param current_user_id: id текущего авторизованного пользователя
    :param queue_id: id очереди
    :return: объект члена очереди

    :raises ForeignKeyViolationException: если очередь с таким id не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства, в котором находится очередь
    :raises UniqueConstraintViolationException: если пара значений user_id и
        queue_id не уникальна
    """

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
    constraint_check: bool = False,
) -> Optional[QueueMember]:
    """
    Функция, реализующая получение члена очереди по user_id и queue_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя
    :param queue_id: id очереди
    :param constraint_check: флаг, определяющий вернется ли None, или
        выбросится исключение
    :return: объект члена очереди, если он существует, None в противном случае

    :raises NoEntityFoundException: если член очереди с таким user_id и
        queue_id не существует
    """

    stmt: Select = select(QueueMember).where(
        QueueMember.user_id == user_id,
        QueueMember.queue_id == queue_id,
    )

    if queue_member := (await session.scalars(stmt)).one_or_none():
        return queue_member
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(
            f"Член очереди с user_id={user_id} и queue_id={queue_id} "
            f"не найден."
        )


async def get_queue_members_by_queue_id(
    session: AsyncSession,
    queue_id: int,
) -> list[QueueMember]:
    """
    Функция, реализующая получение всех членов очереди по queue_id.

    :param session: сессия подключения к БД
    :param queue_id: id очереди
    :return: список членов очереди
    """

    stmt: Select = select(QueueMember).where(QueueMember.queue_id == queue_id)

    return list((await session.scalars(stmt)).all())


# --- Update ---


async def switch_queue_member_status_by_user_id_and_queue_id(
    session: AsyncSession,
    current_user_id: int,
    queue_id: int,
) -> QueueMember:
    """
    Функция, реализующая переключение статуса члена очереди (active/frozen).

    После переключения статуса, оповещает все вебсокеты об изменении очереди.

    :param session: сессия подключения к БД
    :param current_user_id: id текущего авторизованного пользователя
    :param queue_id: id очереди
    :return: обновленный член очереди

    :raises ForeignKeyViolationException: если очередь с таким id не существует
    :raises NoEntityFoundException: если член очереди с таким current_user_id
        и queue_id не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства, в котором находится очередь
    """

    # Комплексная проверка доступа
    queue_member: QueueMember = await complex_queue_member_check(
        session=session,
        current_user_id=current_user_id,
        queue_id=queue_id,
    )

    # Изменение статуса члена очереди
    current_status: str = queue_member.status
    queue_member.status = "active" if current_status == "frozen" else "frozen"
    await session.commit()
    await session.refresh(queue_member)

    # Оповещение подписчиков о новом состоянии очереди
    await manager.notify_subs_about_queue_update(
        session=session,
        queue_id=queue_id,
    )

    return queue_member


# --- Delete ---


async def leave_queue_by_user_id_and_queue_id(
    session: AsyncSession,
    current_user_id: int,
    queue_id: int,
    leave_and_mark: bool = False,
) -> QueueMember:
    """
    Функция, реализующая удаление члена очереди.

    После удаления, оповещает все вебсокеты об изменении очереди.

    :param session: сессия подключения к БД
    :param current_user_id: id текущего авторизованного пользователя
    :param queue_id: id очереди
    :param leave_and_mark: флаг, определяющий помечать ли ближайшее задание
        как сданное после выхода члена очереди
    :return: удаленный член очереди

    :raises ForeignKeyViolationException: если очередь с таким id не существует
    :raises NoEntityFoundException: если член очереди с таким current_user_id
        и queue_id не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является членом рабочего пространства, в котором находится очередь
    """

    # Комплексная проверка доступа
    queue_member: QueueMember = await complex_queue_member_check(
        session=session,
        current_user_id=current_user_id,
        queue_id=queue_id,
    )

    # Удаление члена очереди
    await session.delete(queue_member)
    await session.commit()

    # Получение остальных членов очереди и смещение их позиций
    queue_members: list[QueueMember] = await get_queue_members_by_queue_id(
        session=session,
        queue_id=queue_id,
    )
    for member in queue_members:
        if member.position > queue_member.position:
            member.position -= 1
    await session.commit()

    # Пометка ближайшей работы, если передан флаг
    if leave_and_mark:
        # Получение заданий для предмета, в котором находится очередь
        # noinspection PyTypeChecker
        tasks: list[Task] = await get_tasks_by_subject_id(
            session=session,
            subject_id=(
                await get_queue_by_id(
                    session=session,
                    queue_id=queue_id,
                )
            ).subject_id,
        )

        # Сортировка заданий по id
        tasks.sort(key=lambda t: t.id)

        # Поиск ближайшего не сданного задания
        for task in tasks:
            if not await get_submission_by_user_id_and_task_id(
                session=session,
                user_id=current_user_id,
                task_id=task.id,
            ):
                await create_submission(
                    session=session,
                    task_id=task.id,
                    current_user_id=current_user_id,
                )
                break

    # Оповещение подписчиков о новом состоянии очереди
    await manager.notify_subs_about_queue_update(
        session=session,
        queue_id=queue_id,
    )

    return queue_member
