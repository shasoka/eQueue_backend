"""Модуль, реализующий pydantic-схемы для сущности QueueMember."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

__all__ = (
    "QueueMemberRead",
    "QueueMemberUpdate",
)


class QueueMemberBase(BaseModel):
    """Базовая схема для сущности QueueMember."""

    user_id: int
    queue_id: int
    position: int
    status: Literal["active", "frozen"]


class QueueMemberRead(QueueMemberBase):
    """
    Схема чтения сущности QueueMember.
    Унаследована от базовой схемы QueueMemberBase.
    """

    id: int
    entered_at: datetime


class QueueMemberUpdate(BaseModel):
    """Схема обновления сущности QueueMember."""

    position: Optional[int] = None
    status: Optional[Literal["active", "frozen"]] = None
