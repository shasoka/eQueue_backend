from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models.entities import Subject
from crud.workspaces import check_foreign_key_workspace_id


__all__ = ("get_subjects_from_workspace",)


# --- Проверка ограничений ---


async def check_complex_unique_workspace_id_ecourses_id(
    session: AsyncSession,
    workspace_id: int,
    ecourses_id: int,
) -> None:
    if await get_subject_by_workspace_id_and_ecourses_id(
        session=session,
        workspace_id=workspace_id,
        ecourses_id=ecourses_id,
    ):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"subjects: пара значений workspace_id={workspace_id} и "
            f"ecourses_id={ecourses_id} уже существует в таблице subjects."
        )


async def check_complex_unique_workspace_id_name(
    session: AsyncSession,
    workspace_id: int,
    name: str,
) -> None:
    if await get_subject_by_workspace_id_and_name(
        session=session,
        workspace_id=workspace_id,
        name=name,
    ):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"subjects: пара значений workspace_id={workspace_id} и "
            f"name={name} уже существует в таблице subjects."
        )


# --- Read ---


async def get_subject_by_workspace_id_and_ecourses_id(
    session: AsyncSession,
    workspace_id: int,
    ecourses_id: int,
    constraint_check: bool = True,
) -> Subject | None:
    if subject := (
        await session.scalars(
            select(Subject).where(
                Subject.workspace_id == workspace_id,
                Subject.ecourses_id == ecourses_id,
            )
        )
    ).one_or_none():
        return subject
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(
            f"Предмет с ecourses_id={ecourses_id} и "
            f"workspace_id={workspace_id} не найден"
        )


async def get_subject_by_workspace_id_and_name(
    session: AsyncSession,
    workspace_id: int,
    name: str,
    constraint_check: bool = True,
) -> Subject | None:
    if subject := (
        await session.scalars(
            select(Subject).where(
                Subject.workspace_id == workspace_id,
                Subject.name == name,
            )
        )
    ).one_or_none():
        return subject
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(
            f"Предмет с name={name} и "
            f"workspace_id={workspace_id} не найден"
        )


async def get_subjects_from_workspace(
    session: AsyncSession,
    workspace_id: int,
) -> list[Subject]:
    # Проверка существования рабочего пространства
    await check_foreign_key_workspace_id(session, workspace_id)

    subjects = (
        await session.scalars(
            select(Subject).where(Subject.workspace_id == workspace_id)
        )
    ).all()

    return list(subjects)
