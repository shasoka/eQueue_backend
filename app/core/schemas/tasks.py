from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = ("TaskCreate", "TaskRead", "TaskUpdate")


class TaskBase(BaseModel):
    name: str255
    url: Optional[str255]


class TaskCreate(TaskBase):
    subject_id: int


class TaskRead(TaskBase):
    id: int
    subject_id: int


class TaskReadWithSubmission(TaskRead):
    submitted: bool
    submitted_at: Optional[datetime]


class TaskUpdate(BaseModel):
    name: Optional[str255] = None
    url: Optional[str255] = None
