from typing import List

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    ForeignKeyViolationException,
    GroupIDMismatchException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Group, User, Workspace


from core.schemas.workspace_members import WorkspaceMemberCreate

from core.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
)
from utils import extract_semester_from_group_name

from .groups import check_foreign_key_group_id, get_group_by_id

__all__ = ("create_workspace",)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_workspace_id(
    session: AsyncSession,
    workspace_id: int,
) -> None:
    if not await get_workspace_by_id(session, workspace_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа workspace_id: "
            f"значение {workspace_id} не существует в столбце id таблицы workspaces."
        )


# --- Проверка ограничений ---


async def check_complex_unique_group_id_name(
    session: AsyncSession,
    group_id: int,
    name: str,
) -> None:
    stmt: Select = select(Workspace).where(
        Workspace.group_id == group_id,
        Workspace.name == name,
    )
    if (await session.scalars(stmt)).one_or_none():
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"workspaces: пара значений group_id={group_id} и name={name} уже "
            f"существует в таблице workspaces."
        )


async def check_user_group_id_matches_with_workspace_group_id(
    user_group_id: int | None,
    workspace_group_id: int,
) -> bool:
    if isinstance(user_group_id, int) and user_group_id == workspace_group_id:
        return True
    raise GroupIDMismatchException(
        f"Пользователь с group_id={user_group_id} не может создать рабочее "
        f"пространство для группы с group_id={workspace_group_id}."
    )


# --- Create ---


async def create_workspace(
    session: AsyncSession,
    workspace_in: WorkspaceCreate,
    current_user: User,
) -> WorkspaceRead | None:
    # Распаковка pydantic-модели в SQLAlchemy-модель
    workspace: Workspace = Workspace(**workspace_in.model_dump())

    # --- Ограничение на создание рабочего пространства для пользователя ---

    await check_user_group_id_matches_with_workspace_group_id(
        user_group_id=current_user.group_id,
        workspace_group_id=workspace.group_id,
    )

    # --- Ограничения уникальности ---

    # Проверка существования внешнего ключа group_id
    await check_foreign_key_group_id(session, workspace.group_id)

    # Проверка составного ограничения уникальности group_id и name
    await check_complex_unique_group_id_name(
        session,
        workspace.group_id,
        workspace.name,
    )

    # ---

    # Вычисление текущего семестра по названию группы
    group: Group = await get_group_by_id(
        session,
        workspace.group_id,
        constraint_check=False,
    )
    semester = extract_semester_from_group_name(group.name)

    # Запись рабочего пространства в БД
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)

    # Запись члена рабочего пространства в БД

    # Во избежание циклического импорта
    from .workspace_members import create_workspace_member

    await create_workspace_member(
        session=session,
        workspace_member_in=WorkspaceMemberCreate(
            is_admin=True,
            status="approved",
            user_id=current_user.id,
            workspace_id=workspace.id,
        ),
    )

    return WorkspaceRead(
        id=workspace.id,
        group_id=workspace.group_id,
        name=workspace.name,
        semester=semester,
        members_count=1,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


# --- Read ---


async def get_workspace_by_id(
    session: AsyncSession,
    workspace_id: int,
    constraint_check: bool = True,
) -> WorkspaceRead | None:
    if workspace := await session.get(Workspace, workspace_id):
        # Во избежание циклического импорта
        from .workspace_members import (
            get_workspace_members_count_by_workspace_id,
        )

        # Вычисление текущего семестра по названию группы
        # noinspection PyTypeChecker
        group: Group = await get_group_by_id(
            session,
            workspace.group_id,
            constraint_check=False,
        )
        semester = extract_semester_from_group_name(group.name)

        # noinspection PyTypeChecker
        return WorkspaceRead(
            id=workspace.id,
            name=workspace.name,
            group_id=workspace.group_id,
            semester=semester,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
            members_count=await get_workspace_members_count_by_workspace_id(
                session=session,
                workspace_id=workspace_id,
            ),
        )
    elif constraint_check:
        # Возвращаем None для того, чтобы функция check_foreign_key_workspace_id
        # выбросила свое исключение
        return None
    else:
        # В противном случае выбрасываем исключение, так как рабочее
        # пространство не найдено при попытке его получения
        raise NoEntityFoundException(
            f"Рабочее пространство с id={workspace_id} не найдено"
        )
