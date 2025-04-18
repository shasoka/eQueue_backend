from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import NoEntityFoundException
from core.models import Group

__all__ = ("get_group_by_id",)


async def get_group_by_id(
    session: AsyncSession,
    group_id: int,
) -> Group | None:
    if group := await session.get(Group, group_id):
        return group
    raise NoEntityFoundException(f"Группа с id={group_id} не найден")
