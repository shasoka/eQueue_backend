"""Модуль, реализующий эндпоинты для работы с сущностью User."""

from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    status,
    UploadFile,
)
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import db_helper, User
from core.schemas.users import (
    UserAuth,
    UserCreate,
    UserInfoFromEcourses,
    UserLogin,
    UserRead,
    UserUpdate,
)
from crud.users import (
    create_user,
    get_user_by_ecourses_id,
    get_user_by_id as _get_user_by_id,
    update_user,
)
from docs import generate_responses_for_swagger
from moodle.auth import (
    auth_by_moodle_credentials,
    check_access_token_persistence,
    get_current_user,
    get_moodle_user_info,
)
from moodle.users import upload_new_profile_avatar

__all__ = ("router",)

router = APIRouter()


@router.post(
    settings.api.users.login,
    response_model=UserAuth,
    summary="Авторизация через e.sfu-kras.ru",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        ),
    ),
)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> UserAuth:
    """
    ### Эндпоинт авторизации пользователя через [`e.sfu-kras.ru`](https://e.sfu-kras.ru/).
    \nАвторизация происходит в соответствии со спецификацией `OpenAPI` [`OAuth2`](https://oauth.net/2/).
    \nВходной json должен иметь следующую структуру:
    \n```json\n{\n    \"username\": \"username\",\n    \"password\": \"password\"\n}\n```
    \nВ случае успеха возвращается json с полями:\n```json\n{\n\t\"access_token\": \"token\",\n\t\"token_type\": \"Bearer\",\n\t...\n}\n```
    \nAPI [`e.sfu-kras.ru`](https://e.sfu-kras.ru/) предоставляет метод для авторизации, эндпоинт которого выглядит следующим образом:
    \n***https://e.sfu-kras.ru/login/token.php?service=moodle_mobile_app&username=username&password=password***,
    \nгде `username` и `password` - логин и пароль пользователя в системе электронного обучения СФУ.
    \nПосле авторизации данный эндпоинт получает дополнительные данные пользователя (имя, фамилия, id в системе электронного обучения СФУ) при помощи следующего эндпоинта:
    \n***https://e.sfu-kras.ru/webservice/rest/server.php?wstoken=access_token&wsfunction=core_webservice_get_site_info&moodlewsrestformat=json***, где `access_token` - токен доступа, полученный после авторизации.
    \nПолученный токен в дальнейшем используется как для доступа к данному API, так и для доступа к API [`e.sfu-kras.ru`](https://e.sfu-kras.ru/).
    """

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
            on_login=True,
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


@router.head(
    settings.api.users.alive,
    summary="Пинг токена доступа",
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ),
    ),
)
async def am_i_alive(
    current_user: Annotated[User, Depends(get_current_user)],
) -> ORJSONResponse:
    """
    ### Эндпоинт для проверки активности токена доступа.
    \nПроверяет "жив" ли токен.
    \nВ случае успеха возвращается пустой ответ с заголовком `Token-Alive: true`. В случае неудачи возвращает `403`.
    """

    await check_access_token_persistence(
        access_token=current_user.access_token
    )
    return ORJSONResponse(
        status_code=status.HTTP_200_OK,
        content={},
        headers={"Token-Alive": "true"},
    )


@router.get(
    "",
    response_model=UserRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_404_NOT_FOUND,
        ),
    ),
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Optional[UserRead]:
    return await _get_user_by_id(
        session=session,
        id=current_user.id,
        constraint_check=False,
    )


@router.patch(
    "",
    response_model=UserRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_409_CONFLICT,
        ),
    ),
)
async def partial_update_current_user(
    user_upd: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> User:
    return await update_user(
        session=session,
        user=current_user,
        user_upd=user_upd,
    )


@router.patch(
    settings.api.users.avatar,
    response_model=UserRead,
    responses=generate_responses_for_swagger(
        codes=(
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_409_CONFLICT,
        ),
    ),
)
async def upload_avatar(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    new_profile_pic_url: str = await upload_new_profile_avatar(
        token=current_user.access_token,
        files={
            "filedata": (
                file.filename,
                file.file,
                file.content_type,
            ),
        },
    )
    return await update_user(
        session=session,
        user=current_user,
        user_upd=UserUpdate(
            profile_pic_url=new_profile_pic_url,
        ),
    )
