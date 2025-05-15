from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models.entities import Subject, User
from core.schemas.subjects import SubjectCreate, SubjectUpdate
from crud.workspace_members import (
    check_if_user_is_workspace_admin,
    check_if_user_is_workspace_member,
)
from crud.workspaces import check_foreign_key_workspace_id


__all__ = ("get_subjects_by_workspace_id",)


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


# --- Create ---


async def create_subjects(
    workspace_id: int,
    subjects_in: list[SubjectCreate],
    user_id: int,
    session: AsyncSession,
) -> list[Subject]:

    added_subjects: list[Subject] = []

    for subject in subjects_in:
        # noinspection PyUnresolvedReferences
        # Распаковка pydantic-модели в SQLAlchemy-модель
        subject: Subject = Subject(**subject.model_dump())

        # --- Ограничения уникальности ---

        # Проверка существования рабочего пространства
        await check_foreign_key_workspace_id(
            session=session,
            workspace_id=workspace_id,
        )

        # Проверка является ли пользователь администратором рабочего
        # пространства
        await check_if_user_is_workspace_admin(
            session=session,
            user_id=user_id,
            workspace_id=workspace_id,
        )

        try:
            # Проверка составного ограничения уникальности workspace_id и ecourses_id
            await check_complex_unique_workspace_id_ecourses_id(
                session=session,
                workspace_id=workspace_id,
                ecourses_id=subject.ecourses_id,
            )

            # Проверка составного ограничения уникальности workspace_id и name
            await check_complex_unique_workspace_id_name(
                session=session,
                workspace_id=workspace_id,
                name=subject.name,
            )
        except:
            continue

        # ---

        # workspace_id устанавливается в соответствии с переданным параметром
        subject.workspace_id = workspace_id

        # Запись предмета в БД
        session.add(subject)
        await session.flush()

        added_subjects.append(subject)

    await session.commit()
    return added_subjects


# --- Read ---


async def get_subject_by_id(
    session: AsyncSession,
    subject_id: int,
    constraint_check: bool = True,
    check_membership: bool = False,
    user_id: int = None,
) -> Subject | None:
    if subject := await session.get(Subject, subject_id):
        if check_membership:
            # noinspection PyTypeChecker
            await check_if_user_is_workspace_member(
                session=session,
                user_id=user_id,
                workspace_id=subject.workspace_id,
            )
        return subject
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(f"Предмет с id={subject_id} не найден")


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


async def get_subjects_by_workspace_id(
    session: AsyncSession,
    workspace_id: int,
    check_membership: bool = False,
    user_id: int = None,
) -> list[Subject]:
    # Проверка существования рабочего пространства
    await check_foreign_key_workspace_id(session, workspace_id)

    # Данная функция использутся при получении предметов с еКурсов, где
    # проверка на членство заменена проверкой на администратора.
    # В случае, если данная функция используется в одноименном эндпоинте,
    # проеверяется членство пользователя.

    if check_membership:
        # Проврека является ли пользователь членом рабочего пространства
        await check_if_user_is_workspace_member(
            session=session,
            user_id=user_id,
            workspace_id=workspace_id,
        )

    subjects = (
        await session.scalars(
            select(Subject).where(Subject.workspace_id == workspace_id)
        )
    ).all()

    return list(subjects)


# --- Update ---


async def update_subject(
    session: AsyncSession,
    subject_upd: SubjectUpdate,
    subject_id: int,
    current_user_id: int,
) -> Subject:
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
    )

    # --- Ограничения уникальности ---

    # Проверка является ли пользователь, изменяющий предмет, администратором
    # рабочего пространства, в котором данный предмет находится
    await check_if_user_is_workspace_admin(
        session=session,
        user_id=current_user_id,
        workspace_id=subject.workspace_id,
    )

    # Проверка пришедшего имени предмета на уникальность в рамках данного
    # рабочего пространства
    if subject.name != subject_upd.name:
        await check_complex_unique_workspace_id_name(
            session=session,
            workspace_id=subject.workspace_id,
            name=subject_upd.name,
        )

    # ---

    subject_upd: dict = subject_upd.model_dump(exclude_unset=True)

    for key, value in subject_upd.items():
        setattr(subject, key, value)
    await session.commit()
    await session.refresh(subject)
    return subject


# --- Delete ---


async def delete_subject(
    session: AsyncSession,
    subject_id: int,
    current_user_id: int,
) -> Subject:
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
    )

    # Проверка является ли пользователь, удаляющий предмет, администратором
    # рабочего пространства, в котором данный предмет находится
    await check_if_user_is_workspace_admin(
        session=session,
        user_id=current_user_id,
        workspace_id=subject.workspace_id,
    )

    await session.delete(subject)
    await session.commit()
    return subject
