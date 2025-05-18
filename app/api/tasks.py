from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, Task, User
from core.schemas.tasks import (
    TaskCreate,
    TaskRead,
    TaskReadWithSubmission,
    TaskUpdate,
)

from crud.tasks import (
    create_tasks as _create_tasks,
    delete_task as _delete_task,
    get_task_by_id as _get_task_by_id,
    get_tasks_by_subject_id as _get_tasks_by_subject_id,
    get_tasks_by_subject_id_with_submissions as _get_tasks_by_subject_id_with_submissions,
    get_tasks_from_ecourses,
    update_task,
)
from docs import generate_responses_for_swagger

from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/{sid}",
    response_model=list[TaskRead],
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_tasks(
    sid: int,
    tasks_in: list[TaskCreate],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Task]:
    return await _create_tasks(
        session=session,
        tasks_in=tasks_in,
        subject_id=sid,
        user_id=current_user.id,
    )


@router.get(
    settings.api.tasks.from_ecourses + "/{sid}",
    response_model=list[TaskCreate],
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
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
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
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


@router.get(
    settings.api.tasks.from_subject_with_submissions + "/{sid}",
    response_model=list[TaskReadWithSubmission],
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_tasks_by_subject_id_with_submissions(
    sid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[TaskReadWithSubmission]:
    return await _get_tasks_by_subject_id_with_submissions(
        session=session,
        subject_id=sid,
        current_user=current_user,
    )


@router.get(
    "/{id}",
    response_model=TaskRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_task_by_id(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Optional[Task]:
    return await _get_task_by_id(
        session=session,
        task_id=id,
        constraint_check=False,
        check_membership=True,
        user_id=current_user.id,
    )


@router.patch(
    "/{id}",
    response_model=TaskRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def partial_update_task(
    id: int,
    task_upd: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Task:
    return await update_task(
        session=session,
        task_upd=task_upd,
        task_id=id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{id}",
    response_model=TaskRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def delete_task(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Task:
    return await _delete_task(
        session=session,
        task_id=id,
        current_user_id=current_user.id,
    )
