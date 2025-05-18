from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Submission, User, db_helper
from core.schemas.submissions import SubmissionRead
from crud.submissions import (
    create_submission as _create_submission,
    delete_submission_by_user_id_and_task_id,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/{tid}",
    response_model=SubmissionRead,
    summary="Пометка задания выполненным",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_submission(
    tid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Submission:
    """
    ### Эндпоинт пометки задания как выполненное.
    \nПомечать задания может только член рабочего пространства.
    """

    return await _create_submission(
        session=session,
        task_id=tid,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{tid}",
    response_model=SubmissionRead,
    summary="Удаление пометки задания",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def delete_submission(
    tid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Submission:
    """
    ### Эндпоинт удаления пометки.
    \nУдалять пометку может только член рабочего пространства.
    """

    return await delete_submission_by_user_id_and_task_id(
        session=session,
        user_id=current_user.id,
        task_id=tid,
    )
