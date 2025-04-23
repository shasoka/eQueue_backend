from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User, Workspace
from core.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from crud.workspaces import (
    create_workspace as _create_workspace,
    get_workspace_by_id as _get_workspace_by_id,
    update_workspace,
)

__all__ = ("router",)

from moodle.auth import get_current_user

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
    return await update_workspace(session, workspace_upd, id)
