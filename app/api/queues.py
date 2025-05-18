from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from core.models import db_helper, Queue, User
from core.schemas.queues import QueueCreate, QueueRead, QueueUpdate
from crud.queues import (
    create_queue as _create_queue,
    delete_queue,
    get_queue_by_subject_id as _get_queue_by_subject_id,
    update_queue,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post(
    "",
    response_model=QueueRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_queue(
    queue_in: QueueCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Queue:
    return await _create_queue(
        session=session,
        current_user_id=current_user.id,
        queue_in=queue_in,
    )


@router.get(
    "/{sid}",
    response_model=QueueRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_queue_by_subject_id(
    sid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Queue:
    return await _get_queue_by_subject_id(
        session=session,
        subject_id=sid,
        constraint_check=False,
        check_membership=True,
        user_id=current_user.id,
    )


@router.patch(
    "/{sid}",
    response_model=QueueRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def update_queue_by_subject_id(
    sid: int,
    queue_upd: QueueUpdate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Queue:
    return await update_queue(
        session=session,
        queue_upd=queue_upd,
        subject_id=sid,
        user_id=current_user.id,
    )


@router.delete(
    "/{sid}",
    response_model=QueueRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def delete_queue_by_subject_id(
    sid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Queue:
    return await delete_queue(
        session=session,
        subject_id=sid,
        user_id=current_user.id,
    )
