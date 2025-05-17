from typing import Optional

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    ForeignKeyViolationException,
    GroupIDMismatchException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from core.models import Group, User, Workspace, WorkspaceMember

from core.schemas.workspace_members import WorkspaceMemberCreate

from core.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from utils import extract_semester_from_group_name

from .groups import check_foreign_key_group_id, get_group_by_id

__all__ = (
    "create_workspace",
    "get_workspace_by_id",
    "update_workspace",
)


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
    user_group_id: Optional[int],
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
) -> Optional[WorkspaceRead]:
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
) -> Optional[WorkspaceRead]:
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
            f"Рабочее пространство с id={workspace_id} не найдено."
        )


async def get_workspaces_which_user_is_member_of(
    session: AsyncSession,
    user_id: int,
) -> list[WorkspaceRead]:
    # Во избежание циклического импорта
    from .workspace_members import get_workspace_members_by_user_id

    user_memberships: list[WorkspaceMember] = (
        await get_workspace_members_by_user_id(
            session=session,
            user_id=user_id,
        )
    )

    workspaces: list[WorkspaceRead] = []
    for workspace_member in user_memberships:
        workspaces.append(
            await get_workspace_by_id(
                session=session,
                workspace_id=workspace_member.workspace_id,
            )
        )

    return workspaces


# --- Update ---


async def update_workspace(
    session: AsyncSession,
    workspace_upd: WorkspaceUpdate,
    workspace_id: int,
) -> Optional[WorkspaceRead]:
    # Работаем с orm- и pydantic-моделями из-за динамического поля semester

    # Исключение не заданных явно атрибутов
    workspace_upd: dict = workspace_upd.model_dump(exclude_unset=True)

    workspace_pydantic_model: WorkspaceRead = await get_workspace_by_id(
        session,
        workspace_id,
        constraint_check=False,
    )

    # noinspection PyTypeChecker
    # None не вернется, т.к. эта проверка произошла в get_workspace_by_id
    workspace_orm_model: Workspace = await session.get(Workspace, workspace_id)

    # --- Ограничения уникальности ---

    # Проверка пришедшего имени на уникальность в рамках данной группы
    if (
        "name" in workspace_upd
        and workspace_upd["name"] is not None
        # Если пришло то же имя, что уже записано, то пропускаем проверку
        and workspace_upd["name"] != workspace_orm_model.name
    ):
        await check_complex_unique_group_id_name(
            session,
            workspace_pydantic_model.group_id,
            workspace_upd["name"],
        )

    # ---

    for key, value in workspace_upd.items():
        # Обновление атрибутов в orm-модели
        setattr(workspace_orm_model, key, value)
        # Обновление атрибутов в pydantic-модели
        setattr(workspace_pydantic_model, key, value)
    await session.commit()
    await session.refresh(workspace_orm_model)
    return workspace_pydantic_model


# --- Delete ---


async def delete_workspace(
    session: AsyncSession,
    user_id: int,
    workspace_id: int,
) -> Optional[WorkspaceRead]:
    # Получение рабочего пространства включает проверку на его существование
    workspace_pydantic_model: WorkspaceRead = await get_workspace_by_id(
        session,
        workspace_id,
        constraint_check=False,
    )

    # noinspection PyTypeChecker
    # None не вернется, т.к. эта проверка произошла в get_workspace_by_id
    workspace_orm_model: Workspace = await session.get(Workspace, workspace_id)

    # ---
    # Провека ограничения на удаление рабочего пространства только его
    # администратором
    # ---

    # Во избежание циклического импорта
    from .workspace_members import check_if_user_is_workspace_admin

    await check_if_user_is_workspace_admin(session, user_id, workspace_id)

    # ---

    # Удаление из БД
    await session.delete(workspace_orm_model)
    await session.commit()
    return workspace_pydantic_model
