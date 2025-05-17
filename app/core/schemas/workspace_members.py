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


class WorkspaceMemberLeaderboardEntry(BaseModel):
    user_id: int
    first_name: str255
    second_name: str255
    profile_pic_url: str255
    submissions_count: int


class WorkspaceMemberUpdate(BaseModel):
    status: Optional[Literal["approved", "pending", "rejected"]] = None
