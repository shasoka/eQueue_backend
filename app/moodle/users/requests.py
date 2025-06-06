"""Модуль, содержащий функции для работы с пользователями еКурсов."""

import httpx
from httpx import Response

from core.config import settings
from core.middlewares.logs import logger
from moodle import validate_ecourses_response

from urllib.parse import quote_plus as url_encode


async def upload_new_profile_avatar(
    token: str,
    files: dict,
) -> str:
    """
    Функция, отправляющая файл на сервер Moodle для обновления аватара
    пользователя.

    :param token: access_token пользователя для доступа к методам Moodle
    :param files: словарь, содержащий имя файла, сам файл в байтах и его тип
    :return: строка-ссылка на новый аватар

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    """

    async with httpx.AsyncClient() as client:
        url: str = settings.moodle.upload_file_url % url_encode(token)
        response: Response = await client.post(url, files=files)
        response_json = response.json()

    logger.info(
        "Intermediate request to %s: %s",
        url,
        response_json,
    )

    if not isinstance(response_json, list):
        await validate_ecourses_response(response_json)

    response_data = response_json[0]
    draftitemid = response_data.get("itemid")

    upd_data = {
        "draftitemid": draftitemid,
        "wsfunction": "core_user_update_picture",
        "wstoken": token,
        "moodlewsrestformat": "json",
    }

    # Отправка второго запроса для обновления данных пользователя
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.moodle.ecourses_base_url,
            data=upd_data,
        )
        response_json = response.json()

    logger.info(
        "Intermediate request to %s: %s",
        settings.moodle.ecourses_base_url,
        response_json,
    )

    await validate_ecourses_response(
        response_json, error_key="error", message_key="error"
    )

    return response_json.get("profileimageurl")
