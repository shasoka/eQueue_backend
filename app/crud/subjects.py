"""Модуль, содержащий функции, реализующие CRUD-операции сущности Subject."""

from typing import Optional

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Subject
from core.schemas.subjects import SubjectCreate, SubjectUpdate
from crud.workspace_members import (
    check_if_user_is_workspace_admin,
    check_if_user_is_workspace_member,
)
from crud.workspaces import check_foreign_key_workspace_id

__all__ = (
    "check_foreign_key_subject_id",
    "create_subjects",
    "delete_subject",
    "get_subject_by_id",
    "get_subjects_by_workspace_id",
    "update_subject",
)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_subject_id(
    session: AsyncSession,
    subject_id: int,
) -> None:
    """
    Функция, проверяющая существование внешнего ключа subject_id.

    Используется в CRUD-операциях других сущностей.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД

    :raises ForeignKeyViolationException: если предмет с таким subject_id
        не существует
    """

    if not await get_subject_by_id(session, subject_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа subject_id: "
            f"значение {subject_id} не существует в столбце id таблицы subjects."
        )


# --- Проверка ограничений ---


async def check_complex_unique_workspace_id_ecourses_id(
    session: AsyncSession,
    workspace_id: int,
    ecourses_id: int,
) -> None:
    """
    Функция, проверяющая уникальность пары workspace_id и ecourses_id.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param ecourses_id: id предмета на еКурсах

    :raises UniqueConstraintViolationException: если предмет с такими
        workspace_id и ecourses_id уже существует
    """

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
    """
    Функция, проверяющая уникальность пары workspace_id и name.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param name: наименование предмета

    :raises UniqueConstraintViolationException: если предмет с такими
        workspace_id и name уже существует
    """

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
    """
    Функция, создающая предметы в рабочем пространстве.

    :param workspace_id: id рабочего пространства в БД
    :param subjects_in: объект pydantic-модели SubjectCreate
    :param user_id: id пользователя в БД
    :param session: сессия подключения к БД
    :return: список созданных предметов, если таковые имеются, пустой список в
        противном случае

    :raises ForeignKeyViolationException: если рабочее пространство с таким
        workspace_id не существует
    :raises UserIsNotWorkspaceAdminException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        предмет
    :raises UniqueConstraintViolationException: если предмет с такими
        workspace_id и name/ecourses_id уже существует
    """

    # Проверка существования рабочего пространства
    await check_foreign_key_workspace_id(
        session=session,
        workspace_id=workspace_id,
    )

    added_subjects: list[Subject] = []

    for subject in subjects_in:
        # noinspection PyUnresolvedReferences
        # Распаковка pydantic-модели в SQLAlchemy-модель
        subject: Subject = Subject(**subject.model_dump())

        # --- Ограничения уникальности ---

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
) -> Optional[Subject]:
    """
    Функция, возвращающая предмет по id.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param constraint_check: флаг, определяющий вернется ли None, или
        выбросится исключение
    :param check_membership: флаг, определяющий будет ли произведена проверка
        на принадлежность пользователя к рабочему пространству, в котором
        находится данный предмет
    :param user_id: id пользователя в БД
    :return: предмет, если он существует, None в противном случае

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится предмет
    """

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
        raise NoEntityFoundException(f"Предмет с id={subject_id} не найден.")


async def get_subject_by_workspace_id_and_ecourses_id(
    session: AsyncSession,
    workspace_id: int,
    ecourses_id: int,
) -> Optional[Subject]:
    """
    Функция, возвращающая предмет по workspace_id и ecourses_id.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param ecourses_id: id предмета на еКурсах
    :return: предмет, если он существует, None в противном случае
    """

    stmt: Select = select(Subject).where(
        Subject.workspace_id == workspace_id,
        Subject.ecourses_id == ecourses_id,
    )

    return (await session.scalars(stmt)).one_or_none()


async def get_subject_by_workspace_id_and_name(
    session: AsyncSession,
    workspace_id: int,
    name: str,
) -> Optional[Subject]:
    """
    Функция, возвращающая предмет по workspace_id и name.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param name: наименование предмета
    :return: предмет, если он существует, None в противном случае
    """

    stmt: Select = select(Subject).where(
        Subject.workspace_id == workspace_id,
        Subject.name == name,
    )

    return (await session.scalars(stmt)).one_or_none()


async def get_subjects_by_workspace_id(
    session: AsyncSession,
    workspace_id: int,
    check_membership: bool = False,
    user_id: int = None,
) -> list[Subject]:
    """
    Функция, возвращающая список предметов по workspace_id.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param check_membership: флаг, определяющий будет ли произведена проверка
        на принадлежность пользователя к рабочему пространству
    :param user_id: id пользователя в БД
    :return: список предметов в рабочем пространстве

    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства
    :raises ForeignKeyViolationException: если рабочее пространство с таким
        workspace_id не существует
    """

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
    """
    Функция, обновляющая предмет.

    :param session: сессия подключения к БД
    :param subject_upd: объект pydantic-модели SubjectUpdate
    :param subject_id: id предмета в БД
    :param current_user_id: id пользователя в БД
    :return: обновленный предмет

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится предмет
    :raises ForeignKeyViolationException: если предмет с таким subject_id
        не существует
    :raises UniqueConstraintViolationException: если предмет с таким
        workspace_id и name уже существует
    """

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
    """
    Функция, удаляющая предмет.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param current_user_id: id пользователя в БД
    :return: удаленный предмет

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        предмет
    """

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
