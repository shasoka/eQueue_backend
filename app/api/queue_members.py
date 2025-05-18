from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, QueueMember, User
from core.schemas.queue_members import QueueMemberRead
from crud.queue_members import (
    create_queue_member as _create_queue_member,
    leave_queue_by_user_id_and_queue_id,
    switch_queue_member_status_by_user_id_and_queue_id,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/{qid}",
    response_model=QueueMemberRead,
    summary="Добавление пользователя в очередь",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_queue_member(
    qid: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QueueMember:
    """
    ### Эндпоинт добавления пользователя в очередь.
    \nПользователь может добавить в очередь только себя.
    """

    return await _create_queue_member(
        session=session,
        current_user_id=current_user.id,
        queue_id=qid,
    )


@router.patch(
    "/{qid}",
    response_model=QueueMemberRead,
    summary="Изменение статуса пользователя в очереди",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def partial_update_queue_member(
    qid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> QueueMember:
    """
    ### Эндпоинт изменения статуса пользователя в очереди.
    \nПользователь может изменить статус в очереди только себя.
    \nСтатус меняется на противоположный (`active` / `frozen`).
    """

    return await switch_queue_member_status_by_user_id_and_queue_id(
        session=session,
        current_user_id=current_user.id,
        queue_id=qid,
    )


@router.delete(
    "/{qid}",
    response_model=QueueMemberRead,
    summary="Удаление пользователя из очереди",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def delete_queue_member(
    qid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> QueueMember:
    """
    ### Эндпоинт удаления пользователя из очереди.
    \nПользователь может удалить из очереди только себя.
    """

    return await leave_queue_by_user_id_and_queue_id(
        session=session,
        current_user_id=current_user.id,
        queue_id=qid,
    )


@router.delete(
    settings.api.queue_members.leave_and_mark + "/{qid}",
    response_model=QueueMemberRead,
    summary="Удаление пользователя из очереди и пометка ближайшего задания выполненным",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def delete_queue_member_and_submit_nearest_task(
    qid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> QueueMember:
    """
    ### Эндпоинт удаления пользователя из очереди и пометка ближайшего задания выполненным.
    \nПользователь может удалить из очереди только себя.
    \nБлижайшее задание вычисляется по `id` задания. К примеру, если по предмету существуют задания с `id=(1, 2, 3)` и пользователь сдал задание с `id=2`, то ближайшее задание будет `id=3`. Если таковых заданий не осталось, ничего помечено не будет.
    """

    return await leave_queue_by_user_id_and_queue_id(
        session=session,
        current_user_id=current_user.id,
        queue_id=qid,
        leave_and_mark=True,
    )
