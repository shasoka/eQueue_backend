from typing import List

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    GroupIDMismatchException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Workspace

__all__ = ()

from core.schemas.workspaces import WorkspaceCreate

from crud import check_foreign_key_group_id


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
    current_user_group_id: int | None,
) -> Workspace | None:
    # Распаковка pydantic-модели в SQLAlchemy-модель
    workspace: Workspace = Workspace(**workspace_in.model_dump())

    # --- Ограничение на создание рабочего пространства для пользователя ---

    await check_user_group_id_matches_with_workspace_group_id(
        user_group_id=current_user_group_id,
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

    # Запись рабочего пространства в БД
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    return workspace


# --- Read ---
