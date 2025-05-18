"""
Модуль, реализующий функцию регистрации обработчиков исключений в
FastAPI-приложении.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from core.exceptions import (
    AccessTokenException,
    AdminSuicideException,
    ForeignKeyViolationException,
    GroupIDMismatchException,
    NoEntityFoundException,
    SubjectIsOutOfWorkspaceException,
    UnclassifiedMoodleException,
    UnexpectedWebsocketException,
    UniqueConstraintViolationException,
    UserIsNotWorkspaceAdminException,
)


def register_exceptions_handlers(app: FastAPI) -> None:
    """
    Функция, регистрирующая обработчики исключений в FastAPI-приложении.

    :param app: объект FastAPI
    """

    # noinspection PyUnusedLocal
    @app.exception_handler(UniqueConstraintViolationException)
    async def handle_unique_constraint_violation_exception(
        request: Request,
        exc: UniqueConstraintViolationException,
    ) -> ORJSONResponse:
        """
        Функция, обрабатывающая исключение UniqueConstraintViolationException.
        """

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
        """Функция, обрабатывающая исключение NoEntityFoundException."""

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
        """Функция, обрабатывающая исключение ForeignKeyViolationException."""

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
        """Функция, обрабатывающая исключение UnclassifiedMoodleException."""

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
        """Функция, обрабатывающая исключение AccessTokenException."""

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
        """Функция, обрабатывающая исключение GroupIDMismatchException."""

        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Нарушено ограничение бизнес-логики",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(AdminSuicideException)
    async def handle_access_token_exception(
        request: Request,
        exc: AdminSuicideException,
    ) -> ORJSONResponse:
        """Функция, обрабатывающая исключение AdminSuicideException."""

        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Нарушено ограничение бизнес-логики",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(SubjectIsOutOfWorkspaceException)
    async def handle_subject_is_out_of_workspace_exception(
        request: Request,
        exc: SubjectIsOutOfWorkspaceException,
    ) -> ORJSONResponse:
        """
        Функция, обрабатывающая исключение SubjectIsOutOfWorkspaceException.
        """

        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Нарушено ограничение бизнес-логики",
                "error": str(exc),
            },
        )

    # noinspection PyUnusedLocal
    @app.exception_handler(UnexpectedWebsocketException)
    async def handle_unexpected_websocket_exception(
        request: Request,
        exc: UnexpectedWebsocketException,
    ) -> ORJSONResponse:
        """Функция, обрабатывающая исключение UnexpectedWebsocketException."""

        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": "Неожиданная ошибка в websocket",
                "error": str(exc),
            },
        )
