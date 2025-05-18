"""Модуль, содержащий функции, реализующие CRUD-операции сущности Task."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Subject, Task, User
from core.schemas.tasks import TaskCreate, TaskReadWithSubmission, TaskUpdate
from crud.subjects import check_foreign_key_subject_id, get_subject_by_id
from crud.workspace_members import (
    check_if_user_is_workspace_admin,
    check_if_user_is_workspace_member,
)
from moodle.tasks import get_tasks_from_course_structure

__all__ = (
    "check_foreign_key_task_id",
    "check_if_user_is_permitted_to_get_tasks",
    "check_if_user_is_permitted_to_modify_tasks",
    "create_tasks",
    "delete_task",
    "get_task_by_id",
    "get_tasks_by_subject_id",
    "get_tasks_by_subject_id_with_submissions",
    "get_tasks_from_ecourses",
    "update_task",
)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_task_id(
    session: AsyncSession,
    task_id: int,
) -> None:
    """
    Функция, проверяющая внешний ключ task_id.

    :param session: сессия подключения к БД
    :param task_id: id задания в БД

    :raises ForeignKeyViolationException: если задание с таким task_id не
        существует
    """

    if not await get_task_by_id(session, task_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа task_id: "
            f"значение {task_id} не существует в столбце id таблицы tasks."
        )


# --- Проверка ограничений ---


async def check_complex_unique_subject_id_name(
    session: AsyncSession,
    subject_id: int,
    name: str,
) -> None:
    """
    Функция, проверяющая уникальность пары значений subject_id и name.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param name: наименование задания

    :raises UniqueConstraintViolationException: если пара значений
        subject_id и name уже существует
    """

    if await get_task_by_subject_id_and_name(session, subject_id, name):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"tasks: пара значений subject_id={subject_id} и "
            f"name={name} уже существует в таблице tasks."
        )


async def check_if_user_is_permitted_to_get_tasks(
    session: AsyncSession,
    subject_id: int,
    user_id: int = None,
) -> None:
    """
    Функция, проверяющая является ли пользователь, запришивающий задания,
    членом рабочего пространства, в котором находится данный предмет.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param user_id: id пользователя в БД

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится предмет
    """

    # Получение предмета
    # None не вернется, т.к. уже был передан task
    _ = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
        # Проверка членства пользователя в этой же функции
        check_membership=True,
        user_id=user_id,
    )


async def check_if_user_is_permitted_to_modify_tasks(
    session: AsyncSession,
    subject_id: int,
    user_id: int = None,
) -> None:
    """
    Функция, проверяющая является ли пользователь, запришивающий задания,
    администратором рабочего пространства, в котором находится данный предмет.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param user_id: id пользователя в БД

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        предмет
    """

    # Получение предмета
    # None не вернется, т.к. уже был передан task
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
    )

    # Проверка является ли пользователь администратором рабочего
    # пространства
    await check_if_user_is_workspace_admin(
        session=session,
        user_id=user_id,
        workspace_id=subject.workspace_id,
    )


# --- Create ---


async def create_tasks(
    session: AsyncSession,
    tasks_in: list[TaskCreate],
    subject_id: int,
    user_id: int,
) -> list[Task]:
    """
    Функция, создающая задания.

    :param session: сессия подключения к БД
    :param tasks_in: объект pydantic-модели TaskCreate
    :param subject_id: id предмета в БД
    :param user_id: id пользователя в БД
    :return: список созданных заданий.

    :raises ForeignKeyViolationException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        предмет
    :raises UniqueConstraintViolationException: если пара значений
        subject_id и name уже существует
    """

    # Проверка существования предмета
    await check_foreign_key_subject_id(
        session=session,
        subject_id=subject_id,
    )

    added_tasks: list[Task] = []

    for task in tasks_in:
        # noinspection PyUnresolvedReferences
        # Распаковка pydantic-модели в SQLAlchemy-модель
        task: Task = Task(**task.model_dump())

        # --- Ограничения уникальности ---

        # Проверка является ли пользователь администратором рабочего
        # пространства
        await check_if_user_is_permitted_to_modify_tasks(
            session=session,
            user_id=user_id,
            subject_id=subject_id,
        )

        try:
            # Проверка составного ограничения уникальности workspace_id и ecourses_id
            await check_complex_unique_subject_id_name(
                session=session,
                subject_id=subject_id,
                name=task.name,
            )

        except:
            continue

        # ---

        # subject_id устанавливается в соответствии с переданным параметром
        task.subject_id = subject_id

        # Запись задания в БД
        session.add(task)
        await session.flush()

        added_tasks.append(task)

    await session.commit()
    return added_tasks


# --- Read ---


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
    constraint_check: bool = True,
    check_membership: bool = False,
    user_id: int = None,
) -> Optional[Task]:
    """
    Функция, возвращающая задание по его id.

    :param session: сессия подключения к БД
    :param task_id: id задания в БД
    :param constraint_check: флаг, определяющий, вернется ли None, или
        выбросится исключение
    :param check_membership: флаг, определяющий будет ли произведена проверка
        является ли пользователь членом рабочего пространства
    :param user_id: id пользователя в БД
    :return: задание, если оно существует, иначе None

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится задание
    """

    if task := await session.get(Task, task_id):
        if check_membership:
            # noinspection PyTypeChecker
            await check_if_user_is_permitted_to_get_tasks(
                session=session,
                subject_id=task.subject_id,
                user_id=user_id,
            )
        return task
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(f"Задание с id={task_id} не найдено.")


async def get_task_by_subject_id_and_name(
    session: AsyncSession, subject_id: int, name: str
) -> Optional[Task]:
    """
    Функция, возвращающая задание по его subject_id и name.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param name: наименование задания
    :return: задание, если оно существует, иначе None
    """

    stmt: Select = select(Task).where(
        Task.subject_id == subject_id,
        Task.name == name,
    )

    return (await session.scalars(stmt)).one_or_none()


async def get_tasks_from_ecourses(
    session: AsyncSession,
    target_subject_id: int,
    current_user: User,
) -> list[TaskCreate]:
    """
    Функция, возвращающая задания с еКурсов.

    :param session: сессия подключения к БД
    :param target_subject_id: id предмета в БД
    :param current_user: текущий авторизованный пользователь
    :return: список распаршенных заданий

    :raises NoEntityFoundException: если предмет с таким target_subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        задание
    :raises UnclassifiedMoodleException: если не удалось получить задания с
        еКурсов
    """

    # Получение предмета и проверка его существования
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=target_subject_id,
        constraint_check=False,
    )

    # Проверка является ли пользователь, запришивающий задания,
    # администратором рабочего пространства, в котором находится данный предмет
    await check_if_user_is_workspace_admin(
        session=session,
        user_id=current_user.id,
        workspace_id=subject.workspace_id,
    )

    return await get_tasks_from_course_structure(
        current_user=current_user,
        subject_ecourses_id=subject.ecourses_id,
        subject_id=target_subject_id,
        session=session,
    )


async def get_tasks_by_subject_id(
    session: AsyncSession,
    subject_id: int,
    # При получении лидерборда не требуется проверка членства
    current_user: Optional[User] = None,
) -> list[Task]:
    """
    Функция, возвращающая задания по subject_id.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param current_user: текущий авторизованный пользователь
    :return: список заданий

    :raises NoEntityFoundException: если предмет с таким target_subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится предмет
    """

    # Получение предмета и проверка его существования
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
    )

    if current_user is not None:
        # Проверка является ли пользователь, запришивающий задания,
        # членом рабочего пространства, в котором находится данный предмет
        await check_if_user_is_workspace_member(
            session=session,
            user_id=current_user.id,
            workspace_id=subject.workspace_id,
        )

    stmt: Select = select(Task).where(Task.subject_id == subject_id)
    tasks: list[Task] = list((await session.scalars(stmt)).all())
    return tasks


async def get_tasks_by_subject_id_with_submissions(
    session: AsyncSession,
    subject_id: int,
    current_user: User,
) -> list[TaskReadWithSubmission]:
    """
    Функция, возвращающая задания по subject_id вместе с фактом их сдачи.

    :param session: сессия подключения к БД
    :param subject_id: id предмета в БД
    :param current_user: текущий авторизованный пользователь
    :return: список заданий

    :raises NoEntityFoundException: если предмет с таким subject_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является членом рабочего пространства, в котором находится задание
    """

    # Получение предмета и проверка его существования
    subject: Subject = await get_subject_by_id(
        session=session,
        subject_id=subject_id,
        constraint_check=False,
    )

    # Проверка является ли пользователь, запришивающий задания,
    # членом рабочего пространства, в котором находится данный предмет
    await check_if_user_is_workspace_member(
        session=session,
        user_id=current_user.id,
        workspace_id=subject.workspace_id,
    )

    stmt: Select = (
        select(Task)
        .where(Task.subject_id == subject_id)
        .options(selectinload(Task.submissions))
    )
    tasks: list[Task] = list((await session.execute(stmt)).scalars().all())

    tasks_with_submissions: list[TaskReadWithSubmission] = []

    for task in tasks:
        # Проверяем наличие хотя бы одной submission от текущего пользователя
        submitted: bool = False
        submitted_at: Optional[datetime] = None
        for sub in task.submissions:
            if sub.user_id == current_user.id:
                submitted = True
                submitted_at = sub.submitted_at
                break

        # Формируем объект TaskRead
        task_read = TaskReadWithSubmission(
            id=task.id,
            subject_id=task.subject_id,
            name=task.name,
            url=task.url,
            submitted=submitted,
            submitted_at=submitted_at,
        )
        tasks_with_submissions.append(task_read)

    return tasks_with_submissions


# --- Update ---


async def update_task(
    session: AsyncSession,
    task_upd: TaskUpdate,
    task_id: int,
    current_user_id: int,
) -> Task:
    """
    Функция, обновляющая задание.

    :param session: сессия подключения к БД
    :param task_upd: объект pydantic-модели TaskUpdate
    :param task_id: id задания в БД
    :param current_user_id: id текущего авторизованного пользователя
    :return: обновленное задание

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        задание
    :raises UniqueConstraintViolationException: если пара значений
        subject_id и name уже существует
    """

    task: Task = await get_task_by_id(
        session=session,
        task_id=task_id,
        constraint_check=False,
    )

    # --- Ограничения уникальности ---

    # Проверка является ли пользователь администратором рабочего
    # пространства, в котором находится предмет, задание по которому
    # обновляется
    await check_if_user_is_permitted_to_modify_tasks(
        session=session,
        user_id=current_user_id,
        subject_id=task.subject_id,
    )

    # Проверка пришедшего имени задания на уникальность в рамках данного
    # предмета
    if task.name != task_upd.name:
        await check_complex_unique_subject_id_name(
            session=session,
            subject_id=task.subject_id,
            name=task_upd.name,
        )

    # ---

    task_upd: dict = task_upd.model_dump(exclude_unset=True)

    for key, value in task_upd.items():
        setattr(task, key, value)
    await session.commit()
    await session.refresh(task)
    return task


# --- Delete ---


async def delete_task(
    session: AsyncSession,
    task_id: int,
    current_user_id: int,
) -> Task:
    """
    Функция, удаляющая задание.

    :param session: сессия подключения к БД
    :param task_id: id задания в БД
    :param current_user_id: id текущего авторизованного пользователя
    :return: удаленное задание

    :raises NoEntityFoundException: если задание с таким task_id не
        существует
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        задание
    """

    task: Task = await get_task_by_id(
        session=session,
        task_id=task_id,
        constraint_check=False,
    )

    # Проверка является ли пользователь администратором рабочего
    # пространства, в котором находится предмет, задание по которому
    # удаляется
    await check_if_user_is_permitted_to_modify_tasks(
        session=session,
        user_id=current_user_id,
        subject_id=task.subject_id,
    )

    await session.delete(task)
    await session.commit()
    return task
