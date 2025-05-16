from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, Task, User
from core.schemas.tasks import TaskCreate, TaskRead

from crud.tasks import (
    get_tasks_from_ecourses,
    get_tasks_by_subject_id as _get_tasks_by_subject_id,
    get_task_by_id as _get_task_by_id,
)

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


@router.get(
    settings.api.tasks.from_subject + "/{sid}",
    response_model=list[TaskRead],
)
async def get_tasks_by_subject_id(
    sid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Task]:
    return await _get_tasks_by_subject_id(
        session=session,
        subject_id=sid,
        current_user=current_user,
    )


@router.get("/{id}", response_model=TaskRead)
async def get_task_by_id(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Task | None:
    return await _get_task_by_id(
        session=session,
        task_id=id,
        constraint_check=False,
        check_membership=True,
        user_id=current_user.id,
    )
