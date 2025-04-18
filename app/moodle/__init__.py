from fastapi import HTTPException

from core.exceptions import MoodleTokenException


async def validate(
    response: dict,
    error_key: str = "exception",
    message_key: str = "message",
) -> None:
    """
    Функция, которая получает ответ от еКурсов и проверяет его на предмет
    наличия ошибки.


    Пример ответа от еКурсов:
    .. code-block:: json

            {
                    "error": "Неверный логин или пароль, попробуйте заново.",
                    "errorcode": "invalidlogin",
                    "stacktrace": null,
                    "debuginfo": null,
                    "reproductionlink": null
            }

    :param response: JSON-ответ от еКурсов.
    :param error_key: Ключ, по которому проверяется наличие ошибки.
    :param message_key: Ключ, по которому в JSON находится сообщение об ошибке.
    """

    if error_key in response:
        raise MoodleTokenException(
            "Ответ от еКурсов: " + response[message_key]
        )
