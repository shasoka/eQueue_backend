from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    UploadFile,
    File,
    status,
)
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.users import (
    UserAuth,
    UserInfoFromEcourses,
    UserLogin,
    UserCreate,
    UserUpdate,
    UserRead,
)
from crud.users import (
    get_user_by_ecourses_id,
    create_user,
    update_user,
    get_user_by_id as _get_user_by_id,
)
from moodle.auth import (
    auth_by_moodle_credentials,
    check_access_token_persistence,
    get_current_user,
    get_moodle_user_info,
)

__all__ = ("router",)


router = APIRouter()


@router.post(settings.api.users.login, response_model=UserAuth)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    # Попытка авторизовать пользователя через e.sfu-kras.ru/login
    access_token = await auth_by_moodle_credentials(
        UserLogin(
            login=credentials.username,
            password=credentials.password,
        )
    )

    # При успешной авторизации получаем информацию о пользователе
    user_info: UserInfoFromEcourses = await get_moodle_user_info(
        access_token=access_token
    )

    # Проверка зарегистрирован ли пользователь в системе
    if not (
        registered_user := await get_user_by_ecourses_id(
            session=session,
            ecourses_id=user_info.ecourses_id,
        )
    ):
        # Если пользователь не зарегистрирован, создаем его
        user = await create_user(
            session=session,
            user_in=UserCreate(**(user_info.model_dump())),
        )
    else:
        # Если пользователь зарегистрирован, обновляем его токен
        user = await update_user(
            session=session,
            user=registered_user,
            user_upd=UserUpdate(
                access_token=access_token,
            ),
        )

    # Возвращаем пользователя с access_token и token_type
    return UserAuth.model_validate(user.to_dict()).model_dump()


@router.head(settings.api.users.alive)
async def am_i_alive(
    current_user: Annotated[User, Depends(get_current_user)],
) -> ORJSONResponse:
    await check_access_token_persistence(
        access_token=current_user.access_token
    )
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={},
        headers={"Token-Alive": "true"},
    )


@router.get("/{id}", response_model=UserRead)
async def get_user_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> UserRead | None:
    return await _get_user_by_id(session=session, id=id)
