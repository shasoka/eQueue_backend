from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.tasks import TaskCreate


from crud.tasks import get_tasks_from_ecourses

from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.get(
    settings.api.tasks.from_ecourses + "/{sid}",
    response_model=list[TaskCreate],
)
async def get_tasks_for_subject_from_ecourses(
    sid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[TaskCreate]:
    return await get_tasks_from_ecourses(
        session=session,
        target_subject_id=sid,
        current_user=current_user,
    )
