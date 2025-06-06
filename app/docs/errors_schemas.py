"""Модуль, содержащий схемы ошибок."""

from typing import Any, Union

from fastapi import status

__all__ = ("generate_responses_for_swagger",)

_CODES_DESCRIPTIONS: dict[int, dict[str, str]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Authorization error",
        "message": "Пользователь на авторизован",
        "error": "Ошибка при попытке авторизации в eQueue.",
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Resource forbidden",
        "message": "Ограничение доступа со стороны еКурсов / Нарушено ограничение бизнес-логики / Неожиданная ошибка в websocket",
        "error": "...",
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Resource not found",
        "message": "Сущность не найдена",
        "error": "Сущность с id=... не найдена.",
    },
    status.HTTP_409_CONFLICT: {
        "description": "Resource conflict",
        "message": "Нарушение ограничения внешнего ключа / Нарушено ограничение уникальности / Нарушено ограничение бизнес-логики",
        "error": "...",
    },
}


def generate_error_content_block_for_swagger(
    description: str,
    message: str,
    error: str,
) -> dict[str, Any]:
    """
    Функция, генерирующая схему ошибки для Swagger UI.

    :param description: описание ошибки
    :param message: сообщение ошибки
    :param error: подробное сообщение, переданное в исключение
    :return: схема ошибки для Swagger UI
    """

    return {
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "message": message,
                    "error": error,
                },
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "error": {"type": "string"},
                    },
                },
            },
        },
    }


def generate_responses_for_swagger(
    codes: Union[tuple[int, ...], tuple[Any, ...]],
) -> dict[int, dict[str, Any]]:
    """
    Функция, возвращающая словарь со схемами ошибок для Swagger UI.

    :param codes: кортеж с кодами ошибок
    :return: словарь со схемами ошибок
    """

    responses: dict[int, dict[str, Any]] = {}
    for code in codes:
        responses[code] = generate_error_content_block_for_swagger(
            description=_CODES_DESCRIPTIONS[code]["description"],
            message=_CODES_DESCRIPTIONS[code]["message"],
            error=_CODES_DESCRIPTIONS[code]["error"],
        )

    return responses
