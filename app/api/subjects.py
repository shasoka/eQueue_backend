from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, Subject, User
from core.schemas.subjects import SubjectCreate, SubjectRead, SubjectUpdate
from crud.subjects import (
    create_subjects as _create_subjects,
    delete_subject as _delete_subject,
    get_subject_by_id as _get_subject_by_id,
    get_subjects_by_workspace_id as _get_subjects_by_workspace_id,
    update_subject,
)
from docs import generate_responses_for_swagger
from moodle.auth import get_current_user
from moodle.subjects.requests import get_user_enrolled_courses

__all__ = ("router",)

router = APIRouter()


@router.post(
    "/{wid}",
    response_model=list[SubjectRead],
    summary="Добавление предметов в рабочее пространство",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def create_subjects(
    wid: int,
    subjects_in: list[SubjectCreate],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Subject]:
    """
    ### Эндпоинт добавления предметов в рабочее пространство.
    \nСоздавать предметы может только администратор рабочего пространства.
    \nПредметы всегда добавляются списком, даже если предмет всего один.
    \nВозвращается список добавленных предметов. Предметы, которые по каким-либо причинам не могут быть добавлены пропускаются.
    """

    return await _create_subjects(
        workspace_id=wid,
        subjects_in=subjects_in,
        user_id=current_user.id,
        session=session,
    )


@router.get(
    settings.api.subjects.from_worksapce + "/{wid}",
    response_model=list[SubjectRead],
    summary="Получение списка предметов по ID рабочего пространства",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def get_subjects_by_workspace_id(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Subject]:
    """
    ### Эндпоинт получения списка предметов по ID рабочего пространства.
    \nВозвращается список предметов, которые были добавлены в рабочее пространство.
    """

    return await _get_subjects_by_workspace_id(
        session=session,
        workspace_id=wid,
        check_membership=True,
        user_id=current_user.id,
    )


@router.get(
    settings.api.subjects.from_ecourses + "/{wid}",
    response_model=list[SubjectCreate],
    summary="Получение списка предметов c еКурсов",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def get_enrolled_courses(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[SubjectCreate]:
    """
    ### Эндпоинт получения списка предметов c еКурсов.
    \nКурсы, участником которых является пользователь на еКурсах получаются с помощью REST API еКурсов: ***https://e.sfu-kras.ru/webservice/rest/server.php?wstoken=%s&wsfunction=core_enrol_get_users_courses&moodlewsrestformat=json&userid=%s***.
    \nЗапросить курсы может только администратор рабочего пространства.
    """

    return await get_user_enrolled_courses(
        user=current_user,
        target_workspace_id=wid,
        session=session,
    )


@router.get(
    "/{id}",
    response_model=SubjectRead,
    summary="Получение информации о предмете по ID",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def get_subject_by_id(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Subject:
    """
    ### Эндпоинт получения информации о предмете по ID.
    \nВозвращается предмет, который был добавлен в рабочее пространство.
    \nПолучить информацию о предмете может только член рабочего пространства.
    """

    return await _get_subject_by_id(
        session=session,
        subject_id=id,
        constraint_check=False,
        check_membership=True,
        user_id=current_user.id,
    )


@router.patch(
    "/{id}",
    response_model=SubjectRead,
    summary="Обновление информации о предмете",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_409_CONFLICT,
        )
    ),
)
async def partial_update_subject(
    id: int,
    subject_upd: SubjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Subject:
    """
    ### Эндпоинт обновления информации о предмете.
    \nВозвращает обновленный предмет.
    \nОбновить предмет может только администратор рабочего пространства.
    """

    return await update_subject(
        session=session,
        subject_upd=subject_upd,
        subject_id=id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{id}",
    response_model=SubjectRead,
    summary="Удаление предмета",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )
    ),
)
async def delete_subject(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Subject:
    """
    ### Эндпоинт удаления предмета.
    \nВозвращает удаленный предмет.
    \nУдалить предмет может только администратор рабочего пространства.
    """

    return await _delete_subject(
        session=session,
        subject_id=id,
        current_user_id=current_user.id,
    )
