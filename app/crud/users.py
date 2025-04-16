from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from .groups import get_group_by_id
from core.models import User, Group
from core.schemas.users import UserCreate, UserUpdate
from core.exceptions import ForeignKeyViolation, UniqueConstraintViolation


__all__ = (
    "get_user_by_token",
    "update_user",
    "get_user_by_ecourses_id",
    "create_user",
)

# --- Проверка ограничений ---


async def check_foreign_key_group_id(
    session: AsyncSession, group_id: int
) -> None:
    if not await get_group_by_id(session, group_id):
        raise ForeignKeyViolation(
            f"Нарушено ограничение внешнего ключа group_id: "
            f"значение {group_id} не существует в столбце id таблицы groups."
        )


async def check_unique_ecourses_id(
    session: AsyncSession, ecourses_id: int
) -> None:
    if await get_user_by_ecourses_id(session, ecourses_id):
        raise UniqueConstraintViolation(
            f"Нарушено ограничение уникальности столбца ecourses_id: "
            f"значение {ecourses_id} уже существует в столбце ecourses_id таблицы users."
        )


async def check_unique_token(session: AsyncSession, token: str) -> None:
    if await get_user_by_token(session, token):
        raise UniqueConstraintViolation(
            "Нарушено ограничение уникальности столбца token: "
            "переданное значение токена уже существует в столбце token таблицы users."
        )


# --- Create ---


async def create_user(
    session: AsyncSession,
    user_in: UserCreate,
) -> User | None:
    # Распаковка pydantic-модели в SQLAlchemy-модель
    user: User = User(**user_in.model_dump())

    # --- Ограничения уникальности ---

    # Проверка существования группы до записи пользователя в БД
    if user.group_id:
        await check_foreign_key_group_id(session, user.group_id)

    # Проверка уникальности ecourses_id
    await check_unique_ecourses_id(session, user.ecourses_id)

    # Проверка уникальности token
    await check_unique_token(session, user.token)

    # ---

    # Запись пользователя в БД
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# --- Read ---


async def get_user_by_ecourses_id(
    session: AsyncSession,
    ecourses_id: int,
) -> User | None:
    stmt: Select = select(User).where(User.ecourses_id == ecourses_id)
    return (await session.scalars(stmt)).one_or_none()


async def get_user_by_token(
    session: AsyncSession,
    token: str,
) -> User | None:
    stmt: Select = select(User).where(User.token == token)
    return (await session.scalars(stmt)).one_or_none()


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
