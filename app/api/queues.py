from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Queue, User
from core.schemas.queues import QueueCreate, QueueRead, QueueUpdate
from crud.queues import (
    create_queue as _create_queue,
    update_queue,
    get_queue_by_subject_id as _get_queue_by_subject_id,
    delete_queue,
)
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post("", response_model=QueueRead)
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


@router.get("/{sid}", response_model=QueueRead)
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


@router.patch("/{sid}", response_model=QueueRead)
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


@router.delete("/{sid}", response_model=QueueRead)
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
