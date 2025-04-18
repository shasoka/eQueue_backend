from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from .orm_exceptions import UniqueConstraintViolation, ForeignKeyViolation


def register_exceptions_handlers(app: FastAPI) -> None:

    # noinspection PyUnusedLocal
    @app.exception_handler(UniqueConstraintViolation)
    async def handle_unique_constraint_exception(
        request: Request,
        exc: UniqueConstraintViolation,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Нарушение ограничения уникальности",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(ForeignKeyViolation)
    async def handle_unique_constraint_exception(
        request: Request,
        exc: UniqueConstraintViolation,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Наруешние ограничения внешнего ключа",
                "error": str(exc),
            },
        )
