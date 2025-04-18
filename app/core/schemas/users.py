import datetime

from pydantic import BaseModel


__all__ = (
    "AccessTokenMixin",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "UserAuth",
    "UserLogin",
    "UserInfoFromEcourses",
)


class AccessTokenMixin(BaseModel):
    access_token: str


class UserBase(BaseModel):
    ecourses_id: int
    group_id: int | None = None
    first_name: str
    second_name: str

    # При создании пользователя это поле будет заполнено БД
    profile_status: str | None = None

    profile_pic_url: str


class UserCreate(UserBase, AccessTokenMixin):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserUpdate(BaseModel):
    access_token: str | None = None
    group_id: int | None = None
    profile_status: str | None = None
    profile_pic_url: str | None = None


class UserAuth(UserRead, AccessTokenMixin):
    token_type: str = "Bearer"


class UserLogin(BaseModel):
    login: str
    password: str


class UserInfoFromEcourses(BaseModel):
    access_token: str
    ecourses_id: int
    first_name: str
    second_name: str
    profile_pic_url: str
