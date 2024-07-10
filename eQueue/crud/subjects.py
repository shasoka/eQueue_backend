#  Copyright (c) 2024 Arkady Schoenberg <shasoka@yandex.ru>

from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from core.models import WorkspaceSubject, User
from core.schemas.subjects import WorkspaceSubjectCreate
from crud.workspaces import get_workspace_subject_ids
from moodle.courses import check_course_availability


async def create_workspace_subject(
    session: AsyncSession,
    user: User,
    subject_in: WorkspaceSubjectCreate,
) -> WorkspaceSubject | None:
    if subject_in.workspace_id == user.assigned_workspace_id:
        if check_course_availability(
            course_id=subject_in.ecourses_id,
            token=user.access_token,
        ):
            if subject_in.id not in await get_workspace_subject_ids(
                session,
                user.assigned_group_id,
            ):
                subject = WorkspaceSubject(**subject_in.model_dump())
                session.add(subject)
                await session.commit()
                await session.refresh(subject)
                return subject
            else:
                raise HTTPException(
                    status_code=409,
                    detail=f"Предмет {subject_in.ecourses_id} уже добавлен в рабочее пространство",
                )
        else:
            raise HTTPException(
                status_code=403,
                detail=f"Вы не имеете доступа к предмету {subject_in.ecourses_id}",
            )
    else:
        raise HTTPException(
            status_code=403,
            detail=f"Вы не можете добавлять предметы в рабочее пространство {subject_in.workspace_id}",
        )
