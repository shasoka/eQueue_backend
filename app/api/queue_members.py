from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User
from core.schemas.queue_members import QueueMemberRead
from crud.queue_members import create_queue_member as _create_queue_member
from moodle.auth import get_current_user

router = APIRouter()


@router.post("/{qid}", response_model=QueueMemberRead)
async def create_queue_member(
    qid: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await _create_queue_member(
        session=session,
        current_user_id=current_user.id,
        queue_id=qid,
    )
