from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Submission, User
from core.schemas.submissions import SubmissionRead
from crud.submissions import create_submission as _create_submission
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post("/{tid}", response_model=SubmissionRead)
async def create_submission(
    tid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Submission:
    return await _create_submission(
        session=session,
        task_id=tid,
        current_user_id=current_user.id,
    )
