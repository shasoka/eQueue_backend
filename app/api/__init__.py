from fastapi import APIRouter

from core.config import settings
from .users import router as users_router
from .groups import router as groups_router
from .workspaces import router as workspaces_router
from .workspace_members import router as workspace_members_router
from .subjects import router as subjects_router
from .tasks import router as tasks_router
from .submissions import router as submissions_router
from .queues import router as queues_router
from .queue_members import router as queue_members_router

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

router.include_router(
    router=workspace_members_router,
    prefix=settings.api.workspace_members.prefix,
    tags=settings.api.workspace_members.tags,
)

router.include_router(
    router=subjects_router,
    prefix=settings.api.subjects.prefix,
    tags=settings.api.subjects.tags,
)

router.include_router(
    router=tasks_router,
    prefix=settings.api.tasks.prefix,
    tags=settings.api.tasks.tags,
)

router.include_router(
    router=submissions_router,
    prefix=settings.api.submissions.prefix,
    tags=settings.api.submissions.tags,
)

router.include_router(
    router=queues_router,
    prefix=settings.api.queues.prefix,
    tags=settings.api.queues.tags,
)

router.include_router(
    router=queue_members_router,
    prefix=settings.api.queue_members.prefix,
    tags=settings.api.queue_members.tags,
)
