from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NoEntityFoundException
from core.models import Group

__all__ = ("get_group_by_id", "get_all_groups")


# --- Read ---


async def get_group_by_id(
    session: AsyncSession,
    group_id: int,
) -> Group | None:
    if group := await session.get(Group, group_id):
        return group
    raise NoEntityFoundException(f"Группа с id={group_id} не найдена")


async def get_all_groups(
    session: AsyncSession,
) -> List[Group]:
    return list((await session.execute(select(Group))).scalars().all())


# ---
