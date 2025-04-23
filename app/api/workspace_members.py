from typing import Annotated

from fastapi import APIRouter, Depends

__all__ = ("router",)

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User
from core.schemas.workspace_members import WorkspaceMemberRead
from moodle.auth import get_current_user

from crud.workspace_members import (
    get_workspace_member_by_id as _get_workspace_member_by_id,
)

router = APIRouter()


@router.get("/{id}", response_model=WorkspaceMemberRead)
async def get_workspace_member_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    return await _get_workspace_member_by_id(
        session=session, workspace_member_id=id
    )
