"""Модуль, описывающий исключения websocket'ов."""


class UnexpectedWebsocketException(Exception):
    """
    Кастомное исключение, которое выбрасывается после перехвата неожиданного
    исключения в цикле работы websocket'а.
    """

    pass
