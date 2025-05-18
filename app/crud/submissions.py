"""Модуль, содержащий функции, реализующие CRUD-операции сущности Submission."""

from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    UniqueConstraintViolationException,
)
from core.models import Submission
from crud.tasks import get_task_by_id

__all__ = (
    "create_submission",
    "delete_submission_by_user_id_and_task_id",
    "get_submission_by_user_id_and_task_id",
)


# --- Проверка ограничений ---


async def check_complex_unique_user_id_task_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> None:
    """
    Функция, проверяющая уникальность пары значений user_id и task_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param task_id: id задания в БД

    :raises UniqueConstraintViolationException: если пара значений user_id и
        task_id уже существует
    """

    if await get_submission_by_user_id_and_task_id(session, user_id, task_id):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"submissions: пара значений user_id={user_id} и "
            f"task_id={task_id} уже существует в таблице tasks."
        )


async def check_if_user_is_permitted_to_get_submissions(
    session: AsyncSession,
    task_id: int,
    user_id: int,
) -> None:
    """
    Функция, проверяющая является ли пользователь членом рабочего пространства.

    :param session: сессия подключения к БД
    :param task_id: id задания в БД
    :param user_id: id пользователя в БД

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится задание
    """

    # Здесь же проверяется существование задания
    _ = await get_task_by_id(
        session=session,
        task_id=task_id,
        constraint_check=False,
        check_membership=True,
        user_id=user_id,
    )


# --- Create ---


async def create_submission(
    session: AsyncSession,
    task_id: int,
    current_user_id: int,
) -> Submission:
    """
    Функция, реализующая логику создания помеченного создания.

    :param session: сессия подключения к БД
    :param task_id: id задания в БД
    :param current_user_id: id текущего авторизованного пользователя
    :return: созданное помеченное задание

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится задание
    :raises UniqueConstraintViolationException: если пара значений user_id и
        task_id уже существует
    """

    # Распаковка pydantic-модели в SQLAlchemy-модель
    submission: Submission = Submission(
        task_id=task_id,
        user_id=current_user_id,
    )

    # Проверка является ли пользователь членом рабочего пространства, в
    # котором находится помечаемое задание
    await check_if_user_is_permitted_to_get_submissions(
        session=session,
        task_id=submission.task_id,
        user_id=current_user_id,
    )

    # Проверка внешних ключей

    # Проверка внешнего ключа user_id опущена, т.к. текущий пользователь
    # получен на этапе авторизации

    # Проверка внешнего ключа task_id выполняется в функции
    # check_if_user_is_permitted_to_get_submissions

    # Проверка составного ограничения уникальности
    await check_complex_unique_user_id_task_id(
        session=session,
        user_id=submission.user_id,
        task_id=submission.task_id,
    )

    session.add(submission)
    await session.commit()

    return submission


# --- Read ---


async def get_submission_by_user_id_and_task_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> Optional[Submission]:
    """
    Функция, возвращающая помеченное задание по user_id и task_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param task_id: id задания в БД
    :return: помеченное задание, если оно существует, иначе None
    """

    stmt: Select = select(Submission).where(
        Submission.user_id == user_id,
        Submission.task_id == task_id,
    )

    return (await session.scalars(stmt)).one_or_none()


# --- Delete ---


async def delete_submission_by_user_id_and_task_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> Submission:
    """
    Функция, удаляющая помеченное задание по user_id и task_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param task_id: id задания в БД
    :return: удаленное помеченное задание

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится задание
    """

    # Проверка является ли пользователь членом рабочего пространства, в
    # котором находится помечаемое задание
    await check_if_user_is_permitted_to_get_submissions(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )

    submission: Submission = await get_submission_by_user_id_and_task_id(
        session=session,
        user_id=user_id,
        task_id=task_id,
    )

    await session.delete(submission)
    await session.commit()

    return submission
