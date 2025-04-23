from typing import Annotated, Literal

from fastapi import APIRouter, Depends

__all__ = ("router",)

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User, WorkspaceMember
from core.schemas.workspace_members import WorkspaceMemberRead
from moodle.auth import get_current_user

from crud.workspace_members import (
    get_workspace_member_by_id as _get_workspace_member_by_id,
    get_workspace_members_by_workspace_id_and_status as _get_workspace_members_by_workspace_id_and_status,
)

router = APIRouter()


@router.get("/{id}", response_model=WorkspaceMemberRead)
async def get_workspace_member_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceMember:
    return await _get_workspace_member_by_id(
        session=session, workspace_member_id=id
    )


@router.get(
    settings.api.workspace_members.all + "/{id}/{status}",
    response_model=list[WorkspaceMemberRead],
)
async def get_workspace_members_by_workspace_id_and_status(
    id: int,
    status: Literal["approved", "pending", "rejected"],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[WorkspaceMember]:
    return await _get_workspace_members_by_workspace_id_and_status(
        session=session,
        workspace_id=id,
        user_id=current_user.id,
        status=status,
    )
