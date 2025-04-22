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

    :param session: Сессия подключения к БД.
    :param ecourses_id: Значение столбца ecourses_id.
    :param on_login: Флаг, указывающий, следует ли функции получения пользователя по
                     ecourses_id возвращать None или бросать исключение.
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
    if await get_user_by_access_token(session, access_token, on_login):
        raise UniqueConstraintViolationException(
            "Нарушено ограничение уникальности столбца access_token: "
            "переданное значение токена уже существует в столбце access_token таблицы users."
        )


# --- Create ---


async def create_user(
    session: AsyncSession,
    user_in: UserCreate,
) -> User | None:
    """
    Функция создания новой сущностти пользователя. Вызывается при первом входе пользователя в систему.
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
) -> User | None:
    if user := await session.get(User, id):
        return user
    elif constraint_check:
        # Возвращаем None для того, чтобы функция check_foreign_key_user_id
        # выбросила свое исключение
        return None
    else:
        # В противном случае выбрасываем исключение, так как пользователь не
        # найден при попытке его получения
        raise NoEntityFoundException(f"Пользователь с id={id} не найден")


async def get_user_by_ecourses_id(
    session: AsyncSession, ecourses_id: int, on_login: bool = False
) -> User | None:
    """
    Функция, получающая пользователя по значению столбца ecourses_id.

    Возвращает None, если пользователь впервые авторизуется в системе.

    :param session: Сессия подключения к БД.
    :param ecourses_id: Значение столбца ecourses_id.
    :param on_login: Флаг, указывающий, следует ли функции возвращать None или
                     бросать исключение.
    """

    stmt: Select = select(User).where(User.ecourses_id == ecourses_id)
    if user := (await session.scalars(stmt)).one_or_none():
        return user
    elif on_login:
        return None
    else:
        raise NoEntityFoundException(
            f"Пользователь с ecourses_id={ecourses_id} не найден"
        )


async def get_user_by_access_token(
    session: AsyncSession,
    access_token: str,
    on_login: bool = False,
) -> User | None:
    stmt: Select = select(User).where(User.access_token == access_token)
    if user := (await session.scalars(stmt)).one_or_none():
        return user
    elif on_login:
        return None
    else:
        raise NoEntityFoundException(
            f"Пользователь с таким access_token не найден"
        )


# --- Update ---


async def update_user(
    session: AsyncSession,
    user: User,
    user_upd: UserUpdate,
) -> User | None:
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
