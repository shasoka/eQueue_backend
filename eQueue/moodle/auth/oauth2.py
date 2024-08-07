#  Copyright (c) 2024 Arkady Schoenberg <shasoka@yandex.ru>

from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import User, db_helper
from crud.users import get_user_by_token


class MoodleOAuth2(OAuth2PasswordBearer):

    @staticmethod
    async def validate_token(token: str, session: AsyncSession) -> User | None:
        if not (user := await get_user_by_token(session, token)):
            raise HTTPException(
                status_code=403,
                detail="Пользователь с таким токеном не найден",
                headers={"Token-Alive": "false"},
            )
        return user


oauth2_scheme = MoodleOAuth2(tokenUrl=settings.api.token_url, auto_error=False)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    return await oauth2_scheme.validate_token(token, session)
