"""
Модуль, содержащий функции, реализующие CRUD-операции сущности WorkspaceMember.
"""

from datetime import datetime
from typing import Literal, Optional

from sqlalchemy import func, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import (
    AdminSuicideException,
    NoEntityFoundException,
    SubjectIsOutOfWorkspaceException,
    UniqueConstraintViolationException,
    UserIsNotWorkspaceAdminException,
)
from core.models import Queue, Subject, Task, User, WorkspaceMember
from core.schemas.workspace_members import (
    WorkspaceMemberCreate,
    WorkspaceMemberLeaderboardEntry,
    WorkspaceMemberUpdate,
)
from crud.users import check_foreign_key_user_id, get_user_by_id
from crud.workspaces import check_foreign_key_workspace_id

__all__ = (
    "check_if_user_is_workspace_admin",
    "check_if_user_is_workspace_member",
    "create_workspace_member",
    "delete_workspace_member",
    "get_workspace_member_by_id",
    "get_workspace_members_by_workspace_id_and_status",
    "get_workspace_members_count_by_workspace_id",
    "get_workspace_members_leaderboard_by_subject_submissions_count",
    "update_workspace_member",
)

# --- Проверка ограничений ---


async def check_complex_unique_user_id_workspace_id(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> None:
    """
    Функция, проверяющая уникальность пары значений user_id и workspace_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param workspace_id: id рабочего пространства в БД

    :raises UniqueConstraintViolationException: если пара значений уже
        существует
    """

    if await get_workspace_member_by_user_id_and_workspace_id(
        session,
        user_id,
        workspace_id,
    ):
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"workspace_members: пара значений user_id={user_id} и "
            f"workspace_id={workspace_id} уже существует в таблице workspaces."
        )


async def check_if_user_is_workspace_admin(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> None:
    """
    Функция, проверяющая, является ли пользователь администратором рабочего
    пространства.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param workspace_id: id рабочего пространства в БД

    :raises UserIsNotWorkspaceAdminException: если пользователь не является
        администратором рабочего пространства
    """

    if (
        not (
            member := await get_workspace_member_by_user_id_and_workspace_id(
                session,
                user_id,
                workspace_id,
            )
        )
        or not member.is_admin
    ):
        raise UserIsNotWorkspaceAdminException(
            f"Пользователь с user_id={user_id} не является администратором "
            f"рабочего пространства с workspace_id={workspace_id}."
        )


async def check_if_user_is_workspace_member(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> None:
    """
    Функция, проверяющая, является ли пользователь членом рабочего
    пространства.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param workspace_id: id рабочего пространства в БД

    :raises UserIsNotWorkspaceAdminException: если пользователь не является
        членом рабочего пространства
    """

    if not (
        await get_workspace_member_by_user_id_and_workspace_id(
            session,
            user_id,
            workspace_id,
        )
    ):
        raise UserIsNotWorkspaceAdminException(
            f"Пользователь с user_id={user_id} не является членом рабочего "
            f"пространства с workspace_id={workspace_id}."
        )


# --- Create ---


async def create_workspace_member(
    session: AsyncSession,
    workspace_member_in: WorkspaceMemberCreate,
) -> WorkspaceMember:
    """
    Функция, создающая члена рабочего пространства.

    :param session: сессия подключения к БД
    :param workspace_member_in: объект pydantic-модели WorkspaceMemberCreate
    :return: созданный член рабочего пространства

    :raises UniqueConstraintViolationException: если пара значений user_id и
        workspace_id уже существует
    :raises ForeignKeyViolationException: если внешний ключ
        user_id/workspace_id не существует
    """

    # Распаковка pydantic-модели в SQLAlchemy-модель
    workspace_member: WorkspaceMember = WorkspaceMember(
        **workspace_member_in.model_dump()
    )

    # --- Ограничения уникальности ---

    # Проверка существования внешнего ключа user_id
    await check_foreign_key_user_id(
        session,
        workspace_member.user_id,
    )

    # Проверка существования внешнего ключа workspace_id
    await check_foreign_key_workspace_id(
        session,
        workspace_member.workspace_id,
    )

    # Проверка составного ограничения уникальности user_id и workspace_id
    await check_complex_unique_user_id_workspace_id(
        session,
        workspace_member.user_id,
        workspace_member.workspace_id,
    )

    # ---

    # Запись члена рабочего пространства в БД
    session.add(workspace_member)
    await session.commit()
    await session.refresh(workspace_member)
    return workspace_member


# --- Read ---


async def get_workspace_member_by_user_id_and_workspace_id(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
    constraint_check: bool = True,
) -> Optional[WorkspaceMember]:
    """
    Функция, возвращающая члена рабочего пространства по его user_id и
    workspace_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :param workspace_id: id рабочего пространства в БД
    :param constraint_check: флаг, определяющий, вернется ли None, или
        выбросится исключение
    :return: член рабочего пространства, если он существует, иначе None

    :raises NoEntityFoundException: если член рабочего пространства не
        найден
    """

    if workspace_member := (
        await session.scalars(
            select(WorkspaceMember).where(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.workspace_id == workspace_id,
            )
        )
    ).one_or_none():
        return workspace_member
    elif constraint_check:
        return None
    else:
        raise NoEntityFoundException(
            f"Член рабочего пространства с user_id={user_id} и "
            f"workspace_id={workspace_id} не найден."
        )


async def get_workspace_member_by_id(
    session: AsyncSession,
    workspace_member_id: int,
    check_membership: bool = False,
    current_user_id: Optional[int] = None,
) -> Optional[WorkspaceMember]:
    """
    Функция, возвращающая члена рабочего пространства по его id.

    :param session: сессия подключения к БД
    :param workspace_member_id: id члена рабочего пространства
    :param check_membership: флаг, определяющий будет ли произведена проверка
        является ли пользователь членом рабочего пространства
    :param current_user_id: id текущего авторизованного пользователя
    :return: член рабочего пространства, если он существует, иначе None

    :raises NoEntityFoundException: если член рабочего пространства не
        найден
    :raises UserIsNotWorkspaceAdminException: если пользователь не является
        членом рабочего пространства
    """

    if workspace_member := await session.get(
        WorkspaceMember,
        workspace_member_id,
    ):
        if check_membership:
            # noinspection PyTypeChecker
            await check_if_user_is_workspace_member(
                session=session,
                user_id=current_user_id,
                workspace_id=workspace_member.workspace_id,
            )
        return workspace_member
    raise NoEntityFoundException(
        f"Член рабочего пространства с "
        f"workspace_member_id={workspace_member_id} не найден."
    )


async def get_workspace_members_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> list[WorkspaceMember]:
    """
    Функция, возвращающая членов рабочего пространства по user_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД
    :return: список членств пользователя в рабочих пространствах
    """

    return list(
        (
            await session.execute(
                select(WorkspaceMember).where(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.status == "approved",
                )
            )
        )
        .scalars()
        .all()
    )


async def get_workspace_members_by_workspace_id_and_status(
    session: AsyncSession,
    workspace_id: int,
    user_id: Optional[int] = None,
    status: Literal["approved", "pending", "rejected", "*"] = "approved",
) -> list[WorkspaceMember]:
    """
    Функция, возвращающая членов рабочего пространства по workspace_id и
    status.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства в БД
    :param user_id: id пользователя в БД
    :param status: статус члена рабочего пространства
    :return: список членов рабочего пространства

    :raises ForeignKeyViolationException: если workspace_id не существует
    :raises UserIsNotWorkspaceAdminException: если пользователь не является
        администратором рабочего пространства
    """

    # Проверка существования внешнего ключа workspace_id

    # Во избежание циклического импорта
    from .workspaces import check_foreign_key_workspace_id

    await check_foreign_key_workspace_id(
        session=session,
        workspace_id=workspace_id,
    )

    # Проверка прав администратора, для получения членов рабочего пространства
    # с учетом статуса
    if status in ("pending", "rejected"):
        await check_if_user_is_workspace_admin(
            session=session,
            user_id=user_id,
            workspace_id=workspace_id,
        )

    return list(
        (
            await session.execute(
                select(WorkspaceMember)
                .options(selectinload(WorkspaceMember.user))
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    (
                        WorkspaceMember.status == status
                        if status != "*"
                        else True
                    ),
                )
            )
        )
        .scalars()
        .all()
    )


async def get_workspace_members_count_by_workspace_id(
    session: AsyncSession,
    workspace_id: int,
) -> int:
    """
    Функция, возвращающая количество членов рабочего пространства.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства
    :return: количество членов рабочего пространства
    """

    stmt: Select = (
        select(func.count())
        .select_from(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.status == "approved",
        )
    )
    return (await session.execute(stmt)).scalar_one()


async def get_workspace_members_leaderboard_by_subject_submissions_count(
    session: AsyncSession,
    workspace_id: int,
    user_id: int,
    subject_id: Optional[int] = None,
) -> list[WorkspaceMemberLeaderboardEntry]:
    """
    Функция, возвращающая лидерборд членов рабочего пространства.

    :param session: сессия подключения к БД
    :param workspace_id: id рабочего пространства
    :param user_id: id пользователя
    :param subject_id: id предмета
    :return: лидерборд членов рабочего пространства

    :raises UserIsNotWorkspaceMemberException: если пользователь не является
        членом рабочего пространства
    :raises ForeignKeyViolationException: если workspace_id не существует
    :raises SubjectIsOutOfWorkspaceException: если предмет не принадлежит
        рабочему пространству
    """

    # Проверка того, что пользователь, запрашивающий лидерборд, является
    # членом данного рабочего пространства
    await check_if_user_is_workspace_member(
        session=session,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    # Получаем список членов рабочего пространства, статус которых "approved"
    members: list[WorkspaceMember] = (
        await get_workspace_members_by_workspace_id_and_status(
            session=session,
            workspace_id=workspace_id,
        )
    )

    leaderboard: list[WorkspaceMemberLeaderboardEntry] = []
    for member in members:
        user: User = await get_user_by_id(
            session=session,
            id=member.user_id,
            constraint_check=False,
        )
        leaderboard.append(
            WorkspaceMemberLeaderboardEntry(
                user_id=member.user_id,
                first_name=user.first_name,
                second_name=user.second_name,
                profile_pic_url=user.profile_pic_url,
                submissions_count=0,
            )
        )

    # Если нужен лидерборд по конкретному предмету
    if subject_id is not None:
        # Данная функция вызовет исключение в случае, если такой предмет не
        # найден
        from crud.subjects import get_subject_by_id

        subject: Subject = await get_subject_by_id(
            session=session,
            subject_id=subject_id,
            constraint_check=False,
        )

        if subject.workspace_id != workspace_id:
            raise SubjectIsOutOfWorkspaceException(
                f"Предмет с id={subject_id} не принадлежит рабочему "
                f"пространству с id={workspace_id}."
            )

        # Получаем пул заданий данного предмета
        from crud.tasks import get_tasks_by_subject_id

        tasks: list[Task] = await get_tasks_by_subject_id(
            session=session,
            subject_id=subject.id,
        )

        for member in leaderboard:
            for task in tasks:
                from crud.submissions import (
                    get_submission_by_user_id_and_task_id,
                )

                if await get_submission_by_user_id_and_task_id(
                    session=session,
                    user_id=member.user_id,
                    task_id=task.id,
                ):
                    member.submissions_count += 1
    # Если нужен лидерборд по всем предметам
    else:
        from crud.subjects import get_subjects_by_workspace_id

        subjects: list[Subject] = await get_subjects_by_workspace_id(
            session=session,
            workspace_id=workspace_id,
        )

        for member in leaderboard:
            for subject in subjects:
                from crud.tasks import get_tasks_by_subject_id

                tasks: list[Task] = await get_tasks_by_subject_id(
                    session=session,
                    subject_id=subject.id,
                )

                for task in tasks:
                    from crud.submissions import (
                        get_submission_by_user_id_and_task_id,
                    )

                    if await get_submission_by_user_id_and_task_id(
                        session=session,
                        user_id=member.user_id,
                        task_id=task.id,
                    ):
                        member.submissions_count += 1

    # Сортировка по количеству заданий, фамилии и имени
    return sorted(
        leaderboard,
        key=lambda entry: (
            -entry.submissions_count,
            entry.second_name.lower(),
            entry.first_name.lower(),
        ),
    )


# --- Update ---


async def update_workspace_member(
    session: AsyncSession,
    workspace_member_upd: WorkspaceMemberUpdate,
    workspace_member_id: int,
    current_user_id: int,
) -> WorkspaceMember:
    """
    Функция, обновляющая члена рабочего пространства.

    :param session: сессия подключения к БД
    :param workspace_member_upd: объект pydantic-модели WorkspaceMemberUpdate
    :param workspace_member_id: id члена рабочего пространства
    :param current_user_id: id текущего авторизованного пользователя
    :return: обновленный член рабочего пространства

    :raises NoEntityFoundException: если член рабочего пространства не
        найден
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        член
    """

    # --- Ограничения уникальности ---

    workspace_member: WorkspaceMember = await get_workspace_member_by_id(
        session=session,
        workspace_member_id=workspace_member_id,
    )

    #  Проверка является ли пользователь, изменяющий члена рабочего
    #  пространства, его администратором

    await check_if_user_is_workspace_admin(
        session=session,
        user_id=current_user_id,
        workspace_id=workspace_member.workspace_id,
    )

    # ---

    # Исключение не заданных явно атрибутов
    workspace_member_upd: dict = workspace_member_upd.model_dump(
        exclude_unset=True
    )

    for key, value in workspace_member_upd.items():
        setattr(workspace_member, key, value)
    # Обновление времени присоединения, если статус сменен на approved
    if workspace_member.status == "approved":
        workspace_member.joined_at = datetime.utcnow()
    await session.commit()
    await session.refresh(workspace_member)
    return workspace_member


# --- Delete ---


async def delete_workspace_member(
    session: AsyncSession,
    workspace_member_id: int,
    current_user_id: int,
) -> WorkspaceMember:
    """
    Функция, удаляющая члена рабочего пространства.

    После удаления члена, удаляет связанные записи в таблицах submissions и
    queue_members.

    :param session: сессия подключения к БД
    :param workspace_member_id: id члена рабочего пространства
    :param current_user_id: id текущего авторизованного пользователя
    :return: удаленный пользователь

    :raises NoEntityFoundException: если член рабочего пространства не
        найден
    :raises UserIsNotWorkspaceMemberException: если текущий пользователь не
        является администратором рабочего пространства, в котором находится
        член
    """

    workspace_member: WorkspaceMember = await get_workspace_member_by_id(
        session=session,
        workspace_member_id=workspace_member_id,
    )

    if current_user_id != workspace_member.user_id:
        # Проверка является ли пользователь, удаляющий члена рабочего
        # пространства, его администратором
        await check_if_user_is_workspace_admin(
            session=session,
            user_id=current_user_id,
            workspace_id=workspace_member.workspace_id,
        )

        # Проверка удаления администратора
    if workspace_member.is_admin:
        raise AdminSuicideException(
            f"Член рабочего пространства с id={workspace_member.id} "
            f"является администратором и не может быть удален."
        )

    await session.delete(workspace_member)
    await session.commit()

    # Удаление не связанных по ключу строк из таблицы submissions
    from api.queue_websocket import manager
    from crud.queue_members import get_queue_member_by_user_id_and_queue_id
    from crud.queues import get_queue_by_subject_id
    from crud.subjects import get_subjects_by_workspace_id
    from crud.submissions import get_submission_by_user_id_and_task_id
    from crud.tasks import get_tasks_by_subject_id

    # Получение пула предметов, которые есть в данном рабочем пространстве
    subjects: list[Subject] = await get_subjects_by_workspace_id(
        session=session,
        workspace_id=workspace_member.workspace_id,
    )

    # Получение пула заданий, которые есть в данном рабочем пространстве
    tasks: list[Task] = []
    for subj in subjects:
        tasks.extend(
            await get_tasks_by_subject_id(
                session=session,
                subject_id=subj.id,
            )
        )

    # Поиск и удаление связанных submissions
    for task in tasks:
        if sub := await get_submission_by_user_id_and_task_id(
            session=session,
            user_id=workspace_member.user_id,
            task_id=task.id,
        ):
            await session.delete(sub)
            await session.commit()

    # Удаление не связанных по ключу строк из таблицы queue_members

    # Получение пула очередей, которые есть в данном рабочем пространстве
    queues: list[Queue] = []
    for subj in subjects:
        queue: Queue = await get_queue_by_subject_id(
            session=session,
            subject_id=subj.id,
        )
        if queue:
            queues.append(queue)

    # Поиск и удаление связанных queue_members
    for queue in queues:
        if member := await get_queue_member_by_user_id_and_queue_id(
            session=session,
            user_id=workspace_member.user_id,
            queue_id=queue.id,
            constraint_check=True,
        ):
            await session.delete(member)
            await session.commit()

            # Уведомление подписчиков о обновлении очереди
            await manager.notify_subs_about_queue_update(
                session=session,
                queue_id=queue.id,
            )

    return workspace_member
