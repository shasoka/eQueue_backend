from datetime import datetime
from typing import Literal

from pydantic import BaseModel

__all__ = (
    "WorkspaceMemberCreate",
    "WorkspaceMemberRead",
    "WorkspaceMemberUpdate",
)


class WorkspaceMemberBase(BaseModel):
    is_admin: bool
    status: Literal["approved", "pending", "rejected"]


class WorkspaceMemberCreate(WorkspaceMemberBase):
    user_id: int
    workspace_id: int


class WorkspaceMemberRead(WorkspaceMemberBase):
    id: int
    user_id: int
    workspace_id: int
    joined_at: datetime


class WorkspaceMemberUpdate(BaseModel):
    status: Literal["approved", "pending", "rejected"] | None = None
