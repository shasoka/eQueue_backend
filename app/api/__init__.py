from fastapi import APIRouter

from core.config import settings
from .users import router as users_router
from .groups import router as groups_router
from .workspaces import router as workspaces_router

__all__ = ("router",)


router = APIRouter(prefix=settings.api.prefix)

router.include_router(
    router=users_router,
    prefix=settings.api.users.prefix,
    tags=settings.api.users.tags,
)

router.include_router(
    router=groups_router,
    prefix=settings.api.groups.prefix,
    tags=settings.api.groups.tags,
)

router.include_router(
    router=workspaces_router,
    prefix=settings.api.workspaces.prefix,
    tags=settings.api.workspaces.tags,
)
