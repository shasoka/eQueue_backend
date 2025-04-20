from pydantic import BaseModel


class GroupBase(BaseModel):
    name: str


class GroupRead(GroupBase):
    id: int
