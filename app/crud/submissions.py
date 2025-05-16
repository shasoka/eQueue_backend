from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    SubmissionForbiddenException,
    UniqueConstraintViolationException,
)
from core.models import Submission
from crud.tasks import get_task_by_id


# --- Проверка ограничений ---


async def check_complex_unique_user_id_task_id(
    session: AsyncSession,
    user_id: int,
    task_id: int,
) -> None:
    if await get_submission_by_user_id_and_task_id(session, user_id, task_id):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"submissions: пара значений user_id={user_id} и "
            f"task_id={task_id} уже существует в таблице tasks."
        )


async def check_if_user_is_permitted_to_modify_submissions(
    target_user_id: int,
    current_user_id: int,
) -> None:
    if target_user_id != current_user_id:
        raise SubmissionForbiddenException(
            f"Пользователь с id={current_user_id} не может помечать задания "
            f"пользователя с id={target_user_id}"
        )


async def check_if_user_is_permitted_to_get_submissions(
    session: AsyncSession,
    task_id: int,
    user_id: int,
) -> None:
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
) -> Submission | None:
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
