from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.models.entities import Subject
from core.schemas.subjects import SubjectCreate, SubjectRead, SubjectUpdate
from crud.subjects import (
    get_subjects_by_workspace_id as _get_subjects_by_workspace_id,
    create_subjects as _create_subjects,
    update_subject,
)
from moodle.auth import get_current_user
from moodle.subjects.requests import get_user_enrolled_courses

__all__ = ("router",)

router = APIRouter()


@router.post("/{wid}", response_model=list[SubjectRead])
async def create_subjects(
    wid: int,
    subjects_in: list[SubjectCreate],
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Subject]:
    return await _create_subjects(
        workspace_id=wid,
        subjects_in=subjects_in,
        user_id=current_user.id,
        session=session,
    )


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


@router.get("/{wid}", response_model=list[SubjectRead])
async def get_subjects_by_workspace_id(
    wid: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> list[Subject]:
    return await _get_subjects_by_workspace_id(
        session=session,
        workspace_id=wid,
        check_membership=True,
        user_id=current_user.id,
    )


@router.patch("/{id}", response_model=SubjectRead)
async def partial_update_subject(
    id: int,
    subject_upd: SubjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Subject:
    return await update_subject(
        session=session,
        subject_upd=subject_upd,
        subject_id=id,
        current_user_id=current_user.id,
    )
