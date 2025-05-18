"""Модуль, содержащий функции для работы с заданиями по предметам с еКурсов."""

import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Task, User
from core.schemas.tasks import TaskCreate
from moodle import validate_ecourses_response

from urllib.parse import quote_plus as url_encode


async def _has_duplicate(
    assignments: list[TaskCreate],
    name: str,
) -> bool:
    """
    Функция, проверяющая наличие дубликатов заданий по их именам.

    :param assignments: список заданий
    :param name: наименование задания, по которому происходит сравнение
    :return: True - если дубликат есть, False - если нет
    """

    for assignment in assignments:
        if assignment.name == name:
            return True
    return False


async def get_tasks_from_course_structure(
    current_user: User,
    subject_ecourses_id: int,
    subject_id: int,
    session: AsyncSession,
) -> list[TaskCreate]:
    """
    Функция, которая парсит структуру курса и возвращает список заданий.

    :param current_user: текущий авторизованный пользователь
    :param subject_ecourses_id: id предмета на еКурсах
    :param subject_id: id предмета в БД
    :param session: сессия подключения к БД
    :return: список распаршенных заданий

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    """

    url = settings.moodle.course_structure_url % (
        url_encode(current_user.access_token),
        url_encode(str(subject_ecourses_id)),
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response_json = response.json()

    if not isinstance(response, list):
        await validate_ecourses_response(response_json)

    # Получение уже имеющихся заданий по данному предмету для дальнейшего
    # исключения дубликатов
    from crud.tasks import get_tasks_by_subject_id

    existing_tasks: list[Task] = await get_tasks_by_subject_id(
        session=session,
        subject_id=subject_id,
        current_user=current_user,
    )

    existing_task_names: list[str] = [task.name for task in existing_tasks]

    result = []
    for structure_node in response.json():
        for module in structure_node["modules"]:
            if module["modname"] == "assign":  # assign - прикрепляемое задание
                # Проверка дубликтов в рамках текущего парсинга
                module["name"] = module["name"].strip()
                if await _has_duplicate(
                    result,
                    module["name"],
                ):
                    module["name"] += f" ({structure_node["name"]})"

                # Проверка дубликатов среди уже имеющихся заданий
                if module["name"] in existing_task_names:
                    continue

                result.append(
                    TaskCreate.model_validate(
                        {
                            "subject_id": subject_id,
                            "name": module["name"],
                            "url": module["url"],
                        }
                    )
                )

    return result
