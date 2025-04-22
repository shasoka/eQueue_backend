from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import UniqueConstraintViolationException
from core.models import WorkspaceMember
from core.schemas.workspace_members import WorkspaceMemberCreate
from crud.users import check_foreign_key_user_id
from crud.workspaces import check_foreign_key_workspace_id


# --- Проверка ограничений ---


async def check_complex_unique_user_id_workspace_id(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> None:
    stmt: Select = select(WorkspaceMember).where(
        WorkspaceMember.user_id == user_id,
        WorkspaceMember.workspace_id == workspace_id,
    )
    if (await session.scalars(stmt)).one_or_none():
        raise UniqueConstraintViolationException(
            f"Нарушено комплексное ограничение уникальности в таблице "
            f"workspace_members: пара значений user_id={user_id} и "
            f"workspace_id={workspace_id} уже существует в таблице workspaces."
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
