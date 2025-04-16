from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import ForeignKeyViolation, UniqueConstraintViolation
from core.models import db_helper
from core.schemas.users import (
    UserAuth,
    UserInfoFromEcourses,
    UserLogin,
    UserCreate,
    UserUpdate,
)
from crud.users import get_user_by_ecourses_id, create_user, update_user
from moodle.auth import auth_by_moodle_credentials, get_moodle_user_info

__all__ = ("router",)


router = APIRouter()


@router.post(settings.api.users.login, response_model=UserAuth)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    # Попытка авторизовать пользователя через e.sfu-kras.ru/login
    token = await auth_by_moodle_credentials(
        UserLogin(
            login=credentials.username,
            password=credentials.password,
        )
    )

    # При успешной авторизации получаем информацию о пользователе
    user_info: UserInfoFromEcourses = await get_moodle_user_info(token=token)

    # Проверка зарегистрирован ли пользователь в системе
    if not (
        registered_user := await get_user_by_ecourses_id(
            session=session,
            ecourses_id=user_info.ecourses_id,
        )
    ):
        # Если пользователь не зарегистрирован, создаем его
        try:
            user = await create_user(
                session=session,
                user_in=UserCreate(**(user_info.model_dump())),
            )
        except (ForeignKeyViolation, UniqueConstraintViolation) as e:
            raise HTTPException(status_code=409, detail=str(e))
    else:
        # Если пользователь зарегистрирован, обновляем его токен
        try:
            user = await update_user(
                session=session,
                user=registered_user,
                user_upd=UserUpdate(
                    token=token,
                ),
            )
        except (ForeignKeyViolation, UniqueConstraintViolation) as e:
            raise HTTPException(status_code=409, detail=str(e))

    # Возвращаем пользователя с token и token_type
    return UserAuth.model_validate(user.to_dict()).model_dump()
