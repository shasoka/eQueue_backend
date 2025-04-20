from fastapi import (
    APIRouter,
    Depends,
    File,
    status,
    UploadFile,
)
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Any, Coroutine, List, Sequence

from core.config import settings
from core.models import db_helper, Group, User
from core.schemas.groups import GroupRead
from core.schemas.users import (
    UserAuth,
    UserCreate,
    UserInfoFromEcourses,
    UserLogin,
    UserRead,
    UserUpdate,
)
from crud.groups import get_all_groups, get_group_by_id as _get_group_by_id
from crud.users import (
    create_user,
    get_user_by_ecourses_id,
    get_user_by_id as _get_user_by_id,
    update_user,
)
from docs import login_user_docs
from moodle.auth import (
    auth_by_moodle_credentials,
    check_access_token_persistence,
    get_current_user,
    get_moodle_user_info,
)
from moodle.users import upload_new_profile_avatar

__all__ = ("router",)

router = APIRouter()


@router.get("/{id}", response_model=GroupRead)
async def get_group_by_id(
    id: int,
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Group:
    return await _get_group_by_id(session=session, group_id=id)


@router.get("", response_model=List[GroupRead])
async def get_groups_list(
    _: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> List[Group]:
    return await get_all_groups(session=session)
