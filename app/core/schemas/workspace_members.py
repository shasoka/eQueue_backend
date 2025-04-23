from datetime import datetime

from pydantic import BaseModel

__all__ = ()


class WorkspaceMemberBase(BaseModel):
    is_admin: bool
    status: str


class WorkspaceMemberCreate(WorkspaceMemberBase):
    user_id: int
    workspace_id: int


class WorkspaceMemberRead(WorkspaceMemberBase):
    id: int
    user_id: int
    workspace_id: int
    joined_at: datetime
