from fastapi import APIRouter

from core.config import settings
from .users import router as users_router

__all__ = ("router",)


router = APIRouter(prefix=settings.api.prefix)

router.include_router(
    router=users_router,
    prefix=settings.api.users.prefix,
    tags=settings.api.users.tags,
)
