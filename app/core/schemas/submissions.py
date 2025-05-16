from datetime import datetime

from pydantic import BaseModel

__all__ = ("SubmissionRead", "SubmissionCreate")


class SubmissionBase(BaseModel):
    task_id: int
    user_id: int


class SubmissionRead(SubmissionBase):
    id: int
    submitted_at: datetime


class SubmissionCreate(SubmissionBase):
    pass
