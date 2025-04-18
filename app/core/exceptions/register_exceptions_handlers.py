from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from . import (
    InternalTokenException,
    MoodleTokenException,
    NoEntityFoundException,
)
from .orm_exceptions import (
    UniqueConstraintViolationException,
    ForeignKeyViolationException,
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
        exc: UniqueConstraintViolationException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Наруешние ограничения внешнего ключа",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(MoodleTokenException)
    async def handle_moodle_token_exception(
        request: Request,
        exc: UniqueConstraintViolationException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "Ошибка при попытке авторизации через еКурсы",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(InternalTokenException)
    async def handle_internal_token_exception(
        request: Request,
        exc: InternalTokenException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Ошибка при попытке авторизации в eQueue",
                "error": str(exc),
            },
            headers={"Token-Alive": "false"},
        )
