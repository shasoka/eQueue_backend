from pydantic import BaseModel

from core.schemas import str255

__all__ = ("GroupRead",)


class GroupBase(BaseModel):
    name: str255


class GroupRead(GroupBase):
    id: int
