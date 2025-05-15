import httpx
from urllib.parse import quote_plus as url_encode

from core.config import settings
from core.schemas.tasks import TaskCreate
from moodle import validate_ecourses_response


async def _has_duplicate(
    assignments: list[TaskCreate],
    name: str,
) -> bool:
    for assignment in assignments:
        if assignment.name == name:
            return True
    return False


async def get_tasks_from_course_structure(
    token: str,
    ecourses_id: int,
    subject_id: int,
) -> list[TaskCreate] | None:
    url = settings.moodle.course_structure_url % (
        url_encode(token),
        url_encode(str(ecourses_id)),
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response_json = response.json()

    if not isinstance(response, list):
        await validate_ecourses_response(response_json)

    result = []
    for structure_node in response.json():
        for module in structure_node["modules"]:
            if module["modname"] == "assign":  # assign - прикрепляемое задание
                if await _has_duplicate(
                    result,
                    module["name"],
                ):
                    module["name"] += f" ({structure_node["name"]})"
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
