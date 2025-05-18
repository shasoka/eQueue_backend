"""Модуль, реализующий pydantic-схемы для сущности Task."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "TaskCreate",
    "TaskRead",
    "TaskReadWithSubmission",
    "TaskUpdate",
)


class TaskBase(BaseModel):
    """Базовая схема сущности Task."""

    name: str255
    url: Optional[str255]


class TaskCreate(TaskBase):
    """
    Схема создания сущности Task.
    Унаследована от базовой схемы TaskBase.
    """

    subject_id: int


class TaskRead(TaskBase):
    """
    Схема чтения сущности Task.
    Унаследована от базовой схемы TaskBase.
    """

    id: int
    subject_id: int


class TaskReadWithSubmission(TaskRead):
    """
    Схема чтения сущности Task с информацией о ее сдаче.
    Унаследована от базовой схемы TaskRead.
    """

    submitted: bool
    submitted_at: Optional[datetime]


class TaskUpdate(BaseModel):
    """Схема обновления сущности Task."""

    name: Optional[str255] = None
    url: Optional[str255] = None
