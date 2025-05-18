"""Модуль, реализующий pydantic-схемы для сущности Submission."""

from datetime import datetime

from pydantic import BaseModel

__all__ = ("SubmissionRead",)


class SubmissionBase(BaseModel):
    """Базовая схема для сущности Submission."""

    task_id: int
    user_id: int


class SubmissionRead(SubmissionBase):
    """
    Схема чтения сущности Submission.
    Унаследована от SubmissionBase.
    """

    id: int
    submitted_at: datetime
