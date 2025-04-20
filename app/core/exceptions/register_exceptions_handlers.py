from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from . import (
    AccessTokenException,
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
        exc: ForeignKeyViolationException,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Наруешние ограничения внешнего ключа",
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
                "message": "Пользователь не авторизован",
                "error": str(exc),
            },
            headers={"Token-Alive": "false"},
        )
