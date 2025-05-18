"""Модуль, реализующий pydantic-схемы для сущности Queue."""

from pydantic import BaseModel

__all__ = (
    "QueueCreate",
    "QueueRead",
    "QueueUpdate",
)


class QueueBase(BaseModel):
    """Базовая схема сущности Queue."""

    subject_id: int
    members_can_freeze: bool


class QueueCreate(QueueBase):
    """
    Схема создания сущности Queue.
    Унаследована от базовой схемы QueueBase.
    """

    members_can_freeze: bool = True


class QueueRead(QueueBase):
    """
    Схема чтения сущности Queue.
    Унаследована от базовой схемы QueueBase.
    """

    id: int


class QueueUpdate(BaseModel):
    """Схема обновления сущности Queue."""

    members_can_freeze: bool
