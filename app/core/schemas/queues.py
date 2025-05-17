from pydantic import BaseModel


class QueueBase(BaseModel):
    subject_id: int
    members_can_freeze: bool


class QueueCreate(QueueBase):
    members_can_freeze: bool = True


class QueueRead(QueueBase):
    id: int


class QueueUpdate(QueueBase):
    members_can_freeze: bool
