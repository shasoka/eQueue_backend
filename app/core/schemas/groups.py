from pydantic import BaseModel

__all__ = ("GroupBase", "GroupRead")


class GroupBase(BaseModel):
    name: str


class GroupRead(GroupBase):
    id: int
