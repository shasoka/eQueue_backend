from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Queue, User
from core.schemas.queues import QueueCreate, QueueRead
from crud.queues import create_queue as _create_queue
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
