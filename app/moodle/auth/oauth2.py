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

    @staticmethod
    async def validate_access_token(
        access_token: str, session: AsyncSession
    ) -> Optional[User]:
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
                "Ошибка при попытке авторизации в eQueue"
            )
        return user


oauth2_scheme = MoodleOAuth2(
    tokenUrl=settings.api.access_token_url, auto_error=False
)


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    return await oauth2_scheme.validate_access_token(access_token, session)
