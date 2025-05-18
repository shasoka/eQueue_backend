"""Модуль, реализующий pydantic-схемы для сущности WorkspaceMember."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "WorkspaceMemberCreate",
    "WorkspaceMemberLeaderboardEntry",
    "WorkspaceMemberRead",
    "WorkspaceMemberUpdate",
)


class WorkspaceMemberBase(BaseModel):
    """Базовая схема сущности WorkspaceMember."""

    is_admin: bool
    status: Literal["approved", "pending", "rejected"]


class WorkspaceMemberCreate(WorkspaceMemberBase):
    """
    Схема создания сущности WorkspaceMember.
    Унаследована от WorkspaceMemberBase.
    """

    user_id: int
    workspace_id: int


class WorkspaceMemberRead(WorkspaceMemberBase):
    """
    Схема чтения сущности WorkspaceMember.
    Унаследована от WorkspaceMemberBase.
    """

    id: int
    user_id: int
    workspace_id: int
    joined_at: datetime


class WorkspaceMemberLeaderboardEntry(BaseModel):
    """Схема члена лидерборда рабочего пространства."""

    user_id: int
    first_name: str255
    second_name: str255
    profile_pic_url: str255
    submissions_count: int


class WorkspaceMemberUpdate(BaseModel):
    """Схема обновления сущности WorkspaceMember."""

    status: Optional[Literal["approved", "pending", "rejected"]] = None
