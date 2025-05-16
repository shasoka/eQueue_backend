from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from core.exceptions import (
    SubmissionForbiddenException,
    UnclassifiedMoodleException,
    AdminSuicideException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
    ForeignKeyViolationException,
    GroupIDMismatchException,
    UserIsNotWorkspaceAdminException,
    AccessTokenException,
)


def register_exceptions_handlers(app: FastAPI) -> None:

    # noinspection PyUnusedLocal
    @app.exception_handler(UniqueConstraintViolationException)
    async def handle_unique_constraint_violation_exception(
        request: Request,
        exc: UniqueConstraintViolationException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Нарушение ограничения уникальности",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(NoEntityFoundException)
    async def handle_no_entity_found_exception(
        request: Request,
        exc: NoEntityFoundException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Сущность не найдена",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(ForeignKeyViolationException)
    async def handle_foreign_key_violation_exception(
        request: Request,
        exc: ForeignKeyViolationException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Наруешние ограничения внешнего ключа / сущность не "
                "найдена",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(UnclassifiedMoodleException)
    async def handle_unclassified_moodle_exception(
        request: Request,
        exc: UnclassifiedMoodleException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Ограничение доступа со стороны еКурсов",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(AccessTokenException)
    async def handle_access_token_exception(
        request: Request,
        exc: AccessTokenException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "Пользователь на авторизован",
                "error": str(exc),
            },
            headers={"Token-Alive": "false"},
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(GroupIDMismatchException)
    @app.exception_handler(UserIsNotWorkspaceAdminException)
    async def handle_business_logic_exceptions(
        request: Request,
        exc: GroupIDMismatchException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Доступ запрещен",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(AdminSuicideException)
    async def handle_access_token_exception(
        request: Request,
        exc: AdminSuicideException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Нарушено ограничение бизнес-логики",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(SubmissionForbiddenException)
    async def handle_submission_forbidden_exception(
        request: Request,
        exc: SubmissionForbiddenException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Нарушено ограничение бизнес-логики",
                "error": str(exc),
            },
        )
