"""Модуль, содержащий реализацию базового класса сущности."""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from core.config import settings


def camel_case_to_snake_case(input_str: str) -> str:
    """
    Функция, которая преобразует CamelCase в snake_case.

    Используется для создания имени таблицы.

    :param input_str: входная строка в CamelCase
    :return: строка приведенная к snake_case
    """

    chars = []
    for c_idx, char in enumerate(input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс сущностей."""

    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls):
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    def to_dict(self, cast=False):
        """Метод, собирающий словарь из атрибутов сущности."""

        if not cast:
            return {
                c.name: getattr(self, c.name)
                for c in self.__table__.columns.__iter__()
            }
        else:
            return {
                c.name: str(getattr(self, c.name))
                for c in self.__table__.columns.__iter__()
            }
