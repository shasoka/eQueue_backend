from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import ForeignKeyViolationException
from .groups import get_group_by_id


# --- Проверка ограничений внешних ключей ---


async def check_foreign_key_group_id(
    session: AsyncSession,
    group_id: int,
) -> None:
    if not await get_group_by_id(session, group_id):
        raise ForeignKeyViolationException(
            f"Нарушено ограничение внешнего ключа group_id: "
            f"значение {group_id} не существует в столбце id таблицы groups."
        )
