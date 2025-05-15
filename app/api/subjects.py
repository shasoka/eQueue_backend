__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.subjects import SubjectCreate
from moodle.auth import get_current_user
from moodle.subjects.requests import get_user_enrolled_courses

router = APIRouter()


@router.get(
    settings.api.subjects.from_ecourses + "/{wid}",
    response_model=list[SubjectCreate],
)
async def get_enrolled_courses(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[SubjectCreate]:
    return await get_user_enrolled_courses(
        user=current_user,
        target_workspace_id=wid,
        session=session,
    )
