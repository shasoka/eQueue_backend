from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, Workspace
from core.schemas.users import UserCreate, UserUpdate


async def get_workspace_by_group_id(
		session: AsyncSession,
		current_user: User
) -> Workspace | None:
	stmt = select(Workspace).where(Workspace.group_id == current_user.assigned_group_id)
	result = await session.scalars(stmt)
	return result.first()


async def get_user_by_id(
		session: AsyncSession,
		user_id: int
) -> User | None:
	return await session.get(User, user_id)


# noinspection PyTypeChecker
async def get_user_by_token(
		session: AsyncSession,
		access_token: str
) -> User | None:
	stmt = select(User).where(User.access_token == access_token)
	result = await session.scalars(stmt)
	return result.first()


# noinspection PyTypeChecker
async def get_user_by_ecourses_id(
		session: AsyncSession,
		ecourses_user_id: int
) -> User | None:
	stmt = select(User).where(User.ecourses_user_id == ecourses_user_id)
	result = await session.scalars(stmt)
	return result.first()


async def create_new_user(
		session: AsyncSession,
		user_in: UserCreate
) -> User:
	user = User(**user_in.model_dump())
	session.add(user)
	await session.commit()
	return user


async def update_user(
		session: AsyncSession,
		user: User,
		user_upd: UserUpdate
) -> User:
	for key, value in user_upd.model_dump(exclude_unset=True).items():
		setattr(user, key, value)
	await session.commit()
	return user


async def delete_user(
		session: AsyncSession,
		user: User
) -> None:
	await session.delete(user)
	await session.commit()
