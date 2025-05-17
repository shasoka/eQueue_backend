from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from crud.workspaces import (
    create_workspace as _create_workspace,
    delete_workspace as _delete_workspace,
    get_workspace_by_id as _get_workspace_by_id,
    update_workspace,
    get_workspaces_which_user_is_member_of as _get_workspaces_which_user_is_member_of,
)
from moodle.auth import get_current_user


__all__ = ("router",)


router = APIRouter()


@router.post("", response_model=WorkspaceRead)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    return await _create_workspace(
        session=session,
        workspace_in=workspace_in,
        current_user=current_user,
    )


@router.get(
    settings.api.workspaces.subscribed,
    response_model=list[WorkspaceRead],
)
async def get_workspaces_which_user_is_member_of(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[WorkspaceRead]:
    return await _get_workspaces_which_user_is_member_of(
        session=session,
        user_id=current_user.id,
    )


@router.get("/{id}", response_model=WorkspaceRead)
async def get_workspace_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    return await _get_workspace_by_id(
        session=session,
        workspace_id=id,
        constraint_check=False,
    )


@router.patch("/{id}", response_model=WorkspaceRead)
async def partial_update_workspace(
    id: int,
    workspace_upd: WorkspaceUpdate,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    return await update_workspace(
        session=session,
        workspace_upd=workspace_upd,
        workspace_id=id,
    )


@router.delete("/{id}", response_model=WorkspaceRead)
async def delete_workspace(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Optional[WorkspaceRead]:
    return await _delete_workspace(
        session=session,
        user_id=current_user.id,
        workspace_id=id,
    )
