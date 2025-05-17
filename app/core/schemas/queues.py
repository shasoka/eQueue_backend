from pydantic import BaseModel

__all__ = (
    "QueueCreate",
    "QueueRead",
    "QueueUpdate",
)


class QueueBase(BaseModel):
    subject_id: int
    members_can_freeze: bool


class QueueCreate(QueueBase):
    members_can_freeze: bool = True


class QueueRead(QueueBase):
    id: int


class QueueUpdate(BaseModel):
    members_can_freeze: bool
