from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import InternalAccessTokenException
from core.models import User, db_helper
from crud.users import get_user_by_access_token


class MoodleOAuth2(OAuth2PasswordBearer):

    @staticmethod
    async def validate_access_token(
        access_token: str, session: AsyncSession
    ) -> User | None:
        return await get_user_by_access_token(session, access_token)


oauth2_scheme = MoodleOAuth2(
    tokenUrl=settings.api.access_token_url, auto_error=False
)


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    return await oauth2_scheme.validate_access_token(access_token, session)
