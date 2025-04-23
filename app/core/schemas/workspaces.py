from datetime import datetime

from pydantic import BaseModel

__all__ = (
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "WorkspaceRead",
)


class WorkspaceBase(BaseModel):
    group_id: int
    name: str


class WorkspaceRead(WorkspaceBase):
    id: int
    semester: int
    members_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    name: str | None = None
