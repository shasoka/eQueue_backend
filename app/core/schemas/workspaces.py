from datetime import datetime

from pydantic import BaseModel

__all__ = (
    "WorkspaceRead",
    "WorkspaceCreate",
    "WorkspaceUpdate",
)


class WorkspaceBase(BaseModel):
    group_id: int
    name: str
    semester: int


class WorkspaceRead(WorkspaceBase):
    id: int
    created_at: datetime
    updated_at: datetime


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    group_id: int | None = None
    name: str | None = None
    semester: int | None = None
