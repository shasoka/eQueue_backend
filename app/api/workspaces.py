from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from crud.workspaces import (
    create_workspace as _create_workspace,
    delete_workspace as _delete_workspace,
    get_workspace_by_id as _get_workspace_by_id,
    update_workspace,
    get_workspaces_which_user_is_member_of as _get_workspaces_which_user_is_member_of,
    get_available_workspaces as _get_available_workspaces,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user

__all__ = ("router",)

router = APIRouter()


@router.post(
    "",
    response_model=WorkspaceRead,
    summary="Создание нового рабочего пространства",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    """
    ### Эндпоинт создания рабочего пространства.
    \nID группы рабочего пространства и пользователя, создающего его, должны совпадать.
    \nПосле создания рабочего пространства, пользователь автоматически становится его администратором.
    """

    return await _create_workspace(
        session=session,
        workspace_in=workspace_in,
        current_user=current_user,
    )


@router.get(
    settings.api.workspaces.subscribed,
    response_model=list[WorkspaceRead],
    summary="Получение списка рабочих пространств, в которых пользователь является участником",
    responses=generate_responses_for_swagger(
        codes=(status.HTTP_401_UNAUTHORIZED,)
    ),
)
async def get_workspaces_which_user_is_member_of(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[WorkspaceRead]:
    """
    ### Эндпоинт получения списка рабочих пространств, в которых текуший пользователь является участником.
    \nВозвращаемый список содержит все рабочие пространства, в которых статус пользователя равен 'approved'.
    """

    return await _get_workspaces_which_user_is_member_of(
        session=session,
        user_id=current_user.id,
    )


@router.get(
    settings.api.workspaces.available,
    response_model=list[WorkspaceRead],
    summary="Получение списка доступных рабочих пространств",
    responses=generate_responses_for_swagger(
        codes=(status.HTTP_401_UNAUTHORIZED,)
    ),
)
async def get_available_workspaces(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[WorkspaceRead]:
    """
    ### Эндпоинт получения списка доступных для вступления рабочих пространств.
    \nВозвращаемый список содержит все рабочие пространства, связаные с той же группой, которая установлена у пользователя. Из результирующего списка исключаются рабочие пространства, в которых заявка пользователя еще не одобрена.
    """

    return await _get_available_workspaces(
        session=session,
        current_user=current_user,
    )


@router.get(
    "/{id}",
    response_model=WorkspaceRead,
    summary="Получение информации о рабочем пространстве по ID",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_workspace_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    """
    ### Эндпоинт для получения информации о рабочем пространстве по ID.
    \nВозвращает информацию о рабочем пространстве независимо от того, является ли пользователь его членом.
    """

    return await _get_workspace_by_id(
        session=session,
        workspace_id=id,
        constraint_check=False,
    )


@router.patch(
    "/{id}",
    response_model=WorkspaceRead,
    summary="Обновление рабочего пространства",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def partial_update_workspace(
    id: int,
    workspace_upd: WorkspaceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> WorkspaceRead:
    """
    ### Эндпоинт обновления рабочего пространства.
    \nТолько пользователь, являющийся администратором рабочего пространства, может его удалить.
    \nОбновлению подлежит только поле `name`.
    """

    return await update_workspace(
        session=session,
        workspace_upd=workspace_upd,
        workspace_id=id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{id}",
    response_model=WorkspaceRead,
    summary="Удаление рабочего пространства",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def delete_workspace(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Optional[WorkspaceRead]:
    """
    ### Эндпоинт удаления рабочего пространства.
    \nТолько пользователь, являющийся администратором рабочего пространства, может его удалить.
    """

    return await _delete_workspace(
        session=session,
        user_id=current_user.id,
        workspace_id=id,
    )
