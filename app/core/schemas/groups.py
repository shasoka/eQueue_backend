"""Модуль, реализующий pydantic-схемы для сущности Group."""

from pydantic import BaseModel

from core.schemas import str255

__all__ = ("GroupRead",)


class GroupBase(BaseModel):
    """Базовая схема сущности Group."""

    name: str255


class GroupRead(GroupBase):
    """
    Схема чтения сущности Group.
    Унаследована от GroupBase.
    """

    id: int
