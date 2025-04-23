from sqlalchemy import func, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    NoEntityFoundException,
    UniqueConstraintViolationException,
    UserIsNotWorkspaceAdminException,
)
from core.models import WorkspaceMember
from core.schemas.workspace_members import WorkspaceMemberCreate
from crud.users import check_foreign_key_user_id
from crud.workspaces import check_foreign_key_workspace_id

__all__ = (
    "get_workspace_members_count_by_workspace_id",
    "create_workspace_member",
    "check_if_user_is_workspace_admin",
    "get_workspace_member_by_id",
)

# --- Проверка ограничений ---


async def check_complex_unique_user_id_workspace_id(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> None:
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


# --- Create ---


async def create_workspace_member(
    session: AsyncSession,
    workspace_member_in: WorkspaceMemberCreate,
) -> WorkspaceMember:
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
) -> WorkspaceMember | None:
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
            f"workspace_id={workspace_id} не найден"
        )


async def get_workspace_member_by_id(
    session: AsyncSession,
    workspace_member_id: int,
) -> WorkspaceMember | None:
    if workspace_member := await session.get(
        WorkspaceMember,
        workspace_member_id,
    ):
        return workspace_member
    raise NoEntityFoundException(
        f"Член рабочего пространства с "
        f"workspace_member_id={workspace_member_id} не найден."
    )


async def get_workspace_members_count_by_workspace_id(
    session: AsyncSession,
    workspace_id: int,
) -> int:
    stmt: Select = (
        select(func.count())
        .select_from(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    return (await session.execute(stmt)).scalar_one()
