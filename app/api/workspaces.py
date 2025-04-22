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
from typing import Annotated

from core.config import settings
from core.models import db_helper, User, Workspace

from core.schemas.workspaces import WorkspaceCreate, WorkspaceRead
from crud.workspaces import create_workspace as _create_workspace

__all__ = ("router",)

from moodle.auth import get_current_user

router = APIRouter()


@router.post("", response_model=WorkspaceRead)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Workspace:
    return await _create_workspace(
        session=session,
        workspace_in=workspace_in,
        current_user_group_id=current_user.group_id,
    )
