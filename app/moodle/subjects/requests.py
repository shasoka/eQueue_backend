from urllib.parse import quote_plus as url_encode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User
from core.schemas.subjects import EcoursesSubjectDescription, SubjectCreate
from crud.subjects import get_subjects_by_workspace_id
from crud.workspace_members import check_if_user_is_workspace_admin
from crud.workspaces import check_foreign_key_workspace_id
from moodle import validate_ecourses_response


async def get_user_enrolled_courses(
    user: User,
    target_workspace_id: int,
    session: AsyncSession,
) -> list[SubjectCreate]:
    """
    Функция, возвращающая список предметов с еКурсов.

    :param user:
    :param session:
    :param target_workspace_id:
    :return:
    """

    # Проверка сущестования рабочего пространства
    await check_foreign_key_workspace_id(session, target_workspace_id)

    # Проверка является ли пользователь администратором рабочего пространства,
    # для которого запрашивает курсы
    await check_if_user_is_workspace_admin(
        session, user.id, target_workspace_id
    )

    url = settings.moodle.enrolled_courses_url % (
        url_encode(user.access_token),
        url_encode(str(user.ecourses_id)),
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response_json = response.json()

    if not isinstance(response, list):
        await validate_ecourses_response(response_json)

    # Исключение курсов, уже добавленных в базу данных
    existing_subjects = await get_subjects_by_workspace_id(
        session=session,
        workspace_id=target_workspace_id,
    )
    existing_ids = {sub.ecourses_id for sub in existing_subjects}

    courses = []
    for course in response_json:
        if course.get("lastaccess") is None:
            course["lastaccess"] = -1

        if course["id"] not in existing_ids:
            courses.append(EcoursesSubjectDescription.model_validate(course))

    # Сортировка по приоритету пользователя
    sorted_courses = sorted(
        courses,
        key=lambda c: (
            c.hidden,
            -c.lastaccess,
            not c.isfavourite,
        ),
    )

    return [
        SubjectCreate(
            workspace_id=target_workspace_id,
            ecourses_id=course.id,
            ecourses_link=settings.moodle.course_url % course.id,
            professor_name=None,
            professor_contact=None,
            professor_requirements=None,
            name=course.shortname,
        )
        for course in sorted_courses
    ]
