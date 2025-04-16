import requests

from urllib.parse import quote_plus as url_encode

from core.config import settings
from core.schemas.users import UserLogin, UserInfoFromEcourses
from moodle import validate


async def auth_by_moodle_credentials(credentials: UserLogin) -> str:
    # Отправка запроса
    response = requests.get(
        settings.moodle.auth_url
        % (
            url_encode(credentials.login),  # login
            url_encode(credentials.password),  # password
        ),
    )

    # Получение ответа
    response = response.json()
    # Проверка ответа
    await validate(
        response=response,
        error_key="error",
        message_key="error",
    )

    # Возврат токена
    return response["token"]


async def get_moodle_user_info(token: str) -> UserInfoFromEcourses:
    # Отправка запроса
    response = requests.get(
        settings.moodle.get_user_info_url % url_encode(token),
    )

    # Получение ответа
    response = response.json()
    # Проверка ответа
    await validate(response)

    # Возврат необходимых полей
    return UserInfoFromEcourses(
        token=token,
        ecourses_id=response["userid"],
        first_name=response["firstname"],
        second_name=response["lastname"],
        profile_pic_url=response["userpictureurl"],
    )


async def token_persistence(token: str) -> None:
    response = requests.get(
        settings.moodle.get_user_info_url % url_encode(token),
    )
    response = response.json()
    await validate(response)
