"""Модуль, содержащий функции, реализующие CRUD-операции сущности User."""

from typing import Optional

from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.schemas.users import UserCreate, UserUpdate
from core.exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from .groups import check_foreign_key_group_id

__all__ = (
    "check_foreign_key_user_id",
    "create_user",
    "get_user_by_access_token",
    "get_user_by_ecourses_id",
    "get_user_by_id",
    "update_user",
)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_user_id(
    session: AsyncSession,
    user_id: int,
) -> None:
    """
    Функция, проверяющая внешний ключ user_id.

    :param session: сессия подключения к БД
    :param user_id: id пользователя в БД

    :raises ForeignKeyViolationException: если пользователь с таким user_id не
        существует
    """

    if not await get_user_by_id(session, user_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа user_id: "
            f"значение {user_id} не существует в столбце id таблицы users."
        )


# --- Проверка ограничений ---


async def check_unique_ecourses_id(
    session: AsyncSession,
    ecourses_id: int,
    on_login: bool = False,
) -> None:
    """
    Функция, проверяющая уникальность значения столбца ecourses_id в таблице users.

    :param session: сессия подключения к БД
    :param ecourses_id: значение столбца ecourses_id
    :param on_login: флаг, указывающий, следует ли функции получения пользователя по
        ecourses_id возвращать None или бросать исключение.

    :raises UniqueConstraintViolationException: если пользователь с таким
        ecourses_id уже существует
    """

    if await get_user_by_ecourses_id(session, ecourses_id, on_login):
        raise UniqueConstraintViolationException(
            f"Нарушено ограничение уникальности столбца ecourses_id: "
            f"значение {ecourses_id} уже существует в столбце ecourses_id таблицы users."
        )


async def check_unique_access_token(
    session: AsyncSession,
    access_token: str,
    on_login: bool = False,
) -> None:
    """
    Функция, проверяющая уникальность значения столбца ecourses_id в таблице users.

    :param session: сессия подключения к БД
    :param access_token: access_token пользователя
    :param on_login: флаг, указывающий, следует ли функции получения пользователя по
        ecourses_id возвращать None или бросать исключение.

    :raises UniqueConstraintViolationException: если пользователь с таким
        access_token уже существует
    """

    if await get_user_by_access_token(session, access_token, on_login):
        raise UniqueConstraintViolationException(
            "Нарушено ограничение уникальности столбца access_token: "
            "переданное значение токена уже существует в столбце access_token "
            "таблицы users."
        )


# --- Create ---


async def create_user(
    session: AsyncSession,
    user_in: UserCreate,
) -> Optional[User]:
    """
    Функция создания новой сущностти пользователя.

    Вызывается при первом входе пользователя в систему.

    :param session: сессия подключения к БД
    :param user_in: объект pydantic-модели UserCreate
    :return: созданный пользователь

    :raises UniqueConstraintViolationException: если пользователь с таким
        access_token/ecourses_id уже существует
    """

    # Распаковка pydantic-модели в SQLAlchemy-модель
    user: User = User(**user_in.model_dump())

    # --- Ограничения уникальности ---

    # Проверка группы опущена, т.к. создание пользователя происходит при
    # его первом входе

    # Проверка уникальности ecourses_id
    await check_unique_ecourses_id(session, user.ecourses_id, True)

    # Проверка уникальности access_token
    await check_unique_access_token(session, user.access_token, True)

    # ---

    # Запись пользователя в БД
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# --- Read ---


async def get_user_by_id(
    session: AsyncSession,
    id: int,
    constraint_check: bool = True,
) -> Optional[User]:
    """
    Функция, возвращающая пользователя по его id.

    :param session: сессия подключения к БД
    :param id: id пользователя в БД
    :param constraint_check: флаг, определяющий, вернется ли None, или
        выбросится исключение
    :return: пользователь, если он существует, иначе None

    :raises NoEntityFoundException: если пользователь с таким id не
        существует
    """

    if user := await session.get(User, id):
        return user
    elif constraint_check:
        # Возвращаем None для того, чтобы функция check_foreign_key_user_id
        # выбросила свое исключение
        return None
    else:
        # В противном случае выбрасываем исключение, так как пользователь не
        # найден при попытке его получения
        raise NoEntityFoundException(f"Пользователь с id={id} не найден.")


async def get_user_by_ecourses_id(
    session: AsyncSession, ecourses_id: int, on_login: bool = False
) -> Optional[User]:
    """
    Функция, получающая пользователя по значению столбца ecourses_id.

    Возвращает None, если пользователь впервые авторизуется в системе.

    :param session: сессия подключения к БД
    :param ecourses_id: значение столбца ecourses_id
    :param on_login: флаг, указывающий, следует ли функции возвращать None или
        бросать исключение

    :raises NoEntityFoundException: если пользователь с таким
        ecourses_id не найден
    """

    stmt: Select = select(User).where(User.ecourses_id == ecourses_id)
    if user := (await session.scalars(stmt)).one_or_none():
        return user
    elif on_login:
        return None
    else:
        raise NoEntityFoundException(
            f"Пользователь с ecourses_id={ecourses_id} не найден."
        )


async def get_user_by_access_token(
    session: AsyncSession,
    access_token: str,
    on_login: bool = False,
) -> Optional[User]:
    """
    Функция, получающая пользователя по значению столбца ecourses_id.

    Возвращает None, если пользователь впервые авторизуется в системе.

    :param session: сессия подключения к БД
    :param access_token: access_token пользователя
    :param on_login: флаг, указывающий, следует ли функции возвращать None или
        бросать исключение

    :raises NoEntityFoundException: если пользователь с таким
        access_token не найден
    """

    stmt: Select = select(User).where(User.access_token == access_token)
    if user := (await session.scalars(stmt)).one_or_none():
        return user
    elif on_login:
        return None
    else:
        raise NoEntityFoundException(
            f"Пользователь с таким access_token не найден."
        )


# --- Update ---


async def update_user(
    session: AsyncSession,
    user: User,
    user_upd: UserUpdate,
) -> Optional[User]:
    """
    Функция, обновляющая пользователя.

    :param session: сессия подключения к БД
    :param user: текущий пользователь
    :param user_upd: объект pydantic-модели UserUpdate
    :return: обновленный пользователь

    :raises ForeignKeyViolationException: если группы с user_upd["group_id"]
        не существует
    """

    # Исключение не заданных явно атрибутов
    user_upd: dict = user_upd.model_dump(exclude_unset=True)

    # --- Ограничения уникальности ---

    # Проверка существования группы до записи пользователя в БД
    if "group_id" in user_upd and user_upd["group_id"] is not None:
        await check_foreign_key_group_id(session, user_upd["group_id"])

    # ---

    for key, value in user_upd.items():
        setattr(user, key, value)
    await session.commit()
    await session.refresh(user)
    return user
