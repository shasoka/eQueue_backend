from pydantic import BaseModel

__all__ = ("TaskCreate", "TaskRead", "TaskUpdate")


class TaskBase(BaseModel):
    name: str
    url: str | None


class TaskCreate(TaskBase):
    subject_id: int


class TaskRead(TaskBase):
    id: int
    subject_id: int


class TaskReadWithSubmission(TaskRead):
    submitted: bool


class TaskUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
