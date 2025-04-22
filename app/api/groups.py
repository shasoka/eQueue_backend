from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Group, User
from core.schemas.groups import GroupRead
from crud.groups import get_all_groups, get_group_by_id as _get_group_by_id
from moodle.auth import (
    get_current_user,
)

__all__ = ("router",)

router = APIRouter()


@router.get("/{id}", response_model=GroupRead)
async def get_group_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Group:
    return await _get_group_by_id(
        session=session,
        group_id=id,
        constraint_check=False,
    )


@router.get("", response_model=List[GroupRead])
async def get_groups_list(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> List[Group]:
    return await get_all_groups(session=session)
