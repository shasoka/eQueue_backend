"""Модуль, реализующий pydantic-схемы для сущности User."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "UserAuth",
    "UserCreate",
    "UserInfoFromEcourses",
    "UserLogin",
    "UserRead",
    "UserUpdate",
)


class AccessTokenMixin(BaseModel):
    """Mixin для схемы с токеном."""

    access_token: str255


class UserBase(BaseModel):
    """Базовая схема сущности User."""

    ecourses_id: int
    group_id: Optional[int] = None
    first_name: str255
    second_name: str255

    # При создании пользователя это поле будет заполнено БД
    profile_status: Optional[str255] = None

    profile_pic_url: str255


class UserCreate(UserBase, AccessTokenMixin):
    """
    Схема создания сущности User.
    Унаследована от UserBase и AccessTokenMixin.
    """

    pass


class UserRead(UserBase):
    """
    Схема чтения сущности User.
    Унаследована от UserBase.
    """

    id: int
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Схема обновления сущности User."""

    access_token: Optional[str255] = None
    group_id: Optional[int] = None
    profile_status: Optional[str255] = None
    profile_pic_url: Optional[str255] = None


class UserAuth(UserRead, AccessTokenMixin):
    """
    Схема, возвращаемая после авторизации.
    Унаследована от UserRead и AccessTokenMixin.
    """

    token_type: str255 = "Bearer"


class UserLogin(BaseModel):
    """Схема авторизации пользователя."""

    login: str255
    password: str255


class UserInfoFromEcourses(BaseModel):
    """Схема для данных о пользователе, приходящих с еКурсов."""

    access_token: str255
    ecourses_id: int
    first_name: str255
    second_name: str255
    profile_pic_url: str255
