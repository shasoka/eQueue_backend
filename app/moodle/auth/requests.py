"""Модуль, содержащий функции для работы с авторизацией через еКурсы."""

from urllib.parse import quote_plus as url_encode

import httpx
from httpx import Response

from core.config import settings
from core.middlewares.logs import logger
from core.schemas.users import UserInfoFromEcourses, UserLogin
from moodle import validate_ecourses_response


async def auth_by_moodle_credentials(credentials: UserLogin) -> str:
    """
    Функция, отправляющая запрос на сервер еКурсов для авторизации
    пользователя.

    :param credentials: объект UserLogin с логином и паролем
    :return: access_token авторизованного пользователя в случае успеха, в
        противном случае выбрасывается исключение

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    """

    async with httpx.AsyncClient() as client:
        url: str = settings.moodle.auth_url % (
            url_encode(credentials.login),
            url_encode(credentials.password),
        )

        response = await client.get(url)
        response_json = response.json()

    logger.info(
        "Intermediate request to %s: %s",
        url,
        response_json,
    )

    await validate_ecourses_response(
        response=response_json,
        error_key="error",
        message_key="error",
    )

    return response_json["token"]


async def get_moodle_user_info(access_token: str) -> UserInfoFromEcourses:
    """
    Функция, отправляющая запрос на сервер еКурсов для получения информации
    о пользователе.

    :param access_token: access_token пользователя
    :return: объект UserInfoFromEcourses

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    """

    response_json: dict = await check_access_token_persistence(access_token)

    return UserInfoFromEcourses(
        access_token=access_token,
        ecourses_id=response_json["userid"],
        first_name=response_json["firstname"],
        second_name=response_json["lastname"],
        profile_pic_url=response_json["userpictureurl"],
    )


async def check_access_token_persistence(access_token: str) -> dict:
    """
    Функция, проверяющая "жив" ли access_token.

    :param access_token: access_token пользователя
    :return: json-объект с информацией о пользователе

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    """

    async with httpx.AsyncClient() as client:
        url: str = settings.moodle.get_user_info_url % url_encode(access_token)
        response: Response = await client.get(url)
        response_json: dict = response.json()

    logger.info(
        "[TKN_HLTH_CHCK] Intermediate request to %s: %s",
        url,
        response_json,
    )

    await validate_ecourses_response(response_json)

    return response_json
