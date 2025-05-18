"""Модуль, реализующий OAuth2 авторизацию."""

from typing import Annotated, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import AccessTokenException
from core.models import User, db_helper
from crud.users import get_user_by_access_token
from moodle.auth import check_access_token_persistence


class MoodleOAuth2(OAuth2PasswordBearer):
    """Класс, реализующий кастомную OAuth2 авторизацию через еКурсы."""

    @staticmethod
    async def validate_access_token(
        access_token: str, session: AsyncSession
    ) -> Optional[User]:
        """
        Метод, проверяющий существование пользователя и валидность
        access_token.

        :param access_token: access_token пользователя
        :param session: сессия подключения к БД
        :return: авторизованный пользователь в случае успеха, в противном
            случае выбрасывается исключение

        :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
            сообщение об ошибке
        :raises AccessTokenException: если пользователь с таким access_token
            не найден
        """

        if user := await get_user_by_access_token(
            session=session,
            access_token=access_token,
            on_login=True,
        ):
            # Если пользователь найден, то проверяем его access_token
            # В случае успеха исключение не будет выброшено
            await check_access_token_persistence(access_token)
        else:
            # Если пользователь не найден, то выбрасываем исключение
            raise AccessTokenException(
                "Ошибка при попытке авторизации в eQueue."
            )
        return user


oauth2_scheme = MoodleOAuth2(
    tokenUrl=settings.api.access_token_url, auto_error=False
)


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    """
    Функция, использующаяся для получения текущего пользователя в механизме
    внедрения зависимостей.

    :param access_token: access_token пользователя
    :param session: сессия подключения к БД
    :return: авторизованный пользователь в случае успеха, в противном случае
        выбрасывается исключение

    :raises UnclassifiedMoodleException: если ответ от еКурсов содержит
        сообщение об ошибке
    :raises AccessTokenException: если пользователь с таким access_token не
        найден
    """

    return await oauth2_scheme.validate_access_token(access_token, session)
