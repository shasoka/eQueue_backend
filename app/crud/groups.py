"""Модуль, содержащий функции, реализующие CRUD-операции сущности Group."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
)
from core.models import Group

__all__ = (
    "check_foreign_key_group_id",
    "get_all_groups",
    "get_group_by_id",
)


# --- Проверка ограничений внешнего ключа ---


async def check_foreign_key_group_id(
    session: AsyncSession,
    group_id: int,
) -> None:
    """
    Функция, проверяющая существование внешнего ключа group_id.

    Используется в CRUD-операциях других сущностей.

    :param session: сессия подключения к БД
    :param group_id: id группы в БД

    :raises ForeignKeyViolationException: если группа с таким id не существует
    """

    if not await get_group_by_id(session, group_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа group_id: "
            f"значение {group_id} не существует в столбце id таблицы groups."
        )


# --- Read ---


async def get_group_by_id(
    session: AsyncSession,
    group_id: int,
    constraint_check: bool = True,
) -> Optional[Group]:
    """
    Функция, возвращающая группу по ее id.

    :param session: сессия подключения к БД
    :param group_id: id группы в БД
    :param constraint_check: флаг, определяющий вернется ли None или
        выбросится исключение
    :return: группа с указанным id в случае ее существования, None в противном
        случае

    :raises NoEntityFoundException: если группа не найдена
    """

    if group := await session.get(Group, group_id):
        return group
    elif constraint_check:
        # Возвращаем None для того, чтобы функция check_foreign_key_group_id
        # выбросила свое исключение
        return None
    else:
        # В противном случае выбрасываем исключение, так как группа не
        # найдена при попытке ее получения
        raise NoEntityFoundException(f"Группа с id={group_id} не найдена.")


async def get_all_groups(
    session: AsyncSession,
) -> list[Group]:
    """
    Функция, возвращающая список всех групп.

    :param session: сессия подключения к БД
    :return: список всех групп
    """

    return list((await session.execute(select(Group))).scalars().all())
