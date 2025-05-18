from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User, WorkspaceMember, db_helper
from core.schemas.workspace_members import (
    WorkspaceMemberCreate,
    WorkspaceMemberLeaderboardEntry,
    WorkspaceMemberRead,
    WorkspaceMemberUpdate,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user
from crud.workspace_members import (
    create_workspace_member as _create_workspace_member,
    delete_workspace_member as _delete_workspace_member,
    get_workspace_member_by_id as _get_workspace_member_by_id,
    get_workspace_members_by_workspace_id_and_status as _get_workspace_members_by_workspace_id_and_status,
    get_workspace_members_leaderboard_by_subject_submissions_count,
    update_workspace_member,
)

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/{wid}",
    response_model=WorkspaceMemberRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_workspace_member(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceMember:
    return await _create_workspace_member(
        session=session,
        workspace_member_in=WorkspaceMemberCreate(
            is_admin=False,
            status="pending",
            user_id=current_user.id,
            workspace_id=wid,
        ),
    )


@router.get(
    settings.api.workspace_members.all + "/{id}/{status}",
    response_model=list[WorkspaceMemberRead],
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def get_workspace_members_by_workspace_id_and_status(
    id: int,
    member_status: Literal["approved", "pending", "rejected", "*"],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[WorkspaceMember]:
    return await _get_workspace_members_by_workspace_id_and_status(
        session=session,
        workspace_id=id,
        user_id=current_user.id,
        status=member_status,
    )


@router.get(
    settings.api.workspace_members.leaderboard + "/{wid}",
    response_model=list[WorkspaceMemberLeaderboardEntry],
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def get_workspace_leaderboard_by_subject(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    sid: Optional[int] = None,
) -> list[WorkspaceMemberLeaderboardEntry]:
    return (
        await get_workspace_members_leaderboard_by_subject_submissions_count(
            session=session,
            workspace_id=wid,
            user_id=current_user.id,
            subject_id=sid,
        )
    )


@router.get(
    "/{id}",
    response_model=WorkspaceMemberRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_workspace_member_by_id(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceMember:
    return await _get_workspace_member_by_id(
        session=session,
        workspace_member_id=id,
        check_membership=True,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{id}",
    response_model=WorkspaceMemberRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def partial_update_workspace_member(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    workspace_member_upd: WorkspaceMemberUpdate,
) -> WorkspaceMember:
    return await update_workspace_member(
        session=session,
        workspace_member_upd=workspace_member_upd,
        workspace_member_id=id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/id",
    response_model=WorkspaceMemberRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def delete_workspace_member(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceMember:
    return await _delete_workspace_member(
        session=session,
        workspace_member_id=id,
        current_user_id=current_user.id,
    )
