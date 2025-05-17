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
    group_id: int
    name: str255


class WorkspaceRead(WorkspaceBase):
    id: int
    semester: int
    members_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: Optional[str255] = None
