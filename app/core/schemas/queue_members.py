from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class QueueMemberBase(BaseModel):
    user_id: int
    queue_id: int
    position: int
    status: Literal["active", "frozen"]


class QueueMemberCreate(QueueMemberBase):
    status: Literal["active", "frozen"] = "active"


class QueueMemberRead(QueueMemberBase):
    id: int
    entered_at: datetime


class QueueMemberUpdate(BaseModel):
    position: Optional[int] = None
    status: Optional[Literal["active", "frozen"]] = None
