import httpx
from urllib.parse import quote_plus as url_encode

from httpx import Response

from core.config import settings
from core.schemas.users import UserLogin, UserInfoFromEcourses
from moodle import validate

from core.middlewares.logs import logger


async def auth_by_moodle_credentials(credentials: UserLogin) -> str:
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

    await validate(
        response=response_json,
        error_key="error",
        message_key="error",
    )

    return response_json["token"]


async def get_moodle_user_info(token: str) -> UserInfoFromEcourses:
    response_json: dict = await check_token_persistence(token)

    return UserInfoFromEcourses(
        token=token,
        ecourses_id=response_json["userid"],
        first_name=response_json["firstname"],
        second_name=response_json["lastname"],
        profile_pic_url=response_json["userpictureurl"],
    )


async def check_token_persistence(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        url: str = settings.moodle.get_user_info_url % url_encode(token)
        response: Response = await client.get(url)
        response_json: dict = response.json()

    logger.info(
        "Intermediate request to %s: %s",
        url,
        response_json,
    )

    await validate(response_json)

    return response_json
