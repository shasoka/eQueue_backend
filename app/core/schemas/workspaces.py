"""Модуль, реализующий pydantic-схемы для сущности Workspace."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "WorkspaceCreate",
    "WorkspaceRead",
    "WorkspaceUpdate",
)


class WorkspaceBase(BaseModel):
    """Базовая схема сущности Workspace."""

    group_id: int
    name: str255


class WorkspaceRead(WorkspaceBase):
    """Схема чтения сущности Workspace."""

    id: int
    semester: int
    members_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceCreate(WorkspaceBase):
    """
    Схема создания сущности Workspace.
    Унаследована от базовой схемы WorkspaceBase.
    """

    pass


class WorkspaceUpdate(BaseModel):
    """Схема обновления сущности Workspace."""

    name: Optional[str255] = None
