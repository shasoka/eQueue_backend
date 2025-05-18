"""
Пакет, содержащий описание кастомных исключений и функцию регистрации их
обработчиков.
"""

from .business_logic_exceptions import (
    AdminSuicideException,
    GroupIDMismatchException,
    SubjectIsOutOfWorkspaceException,
    UserIsNotWorkspaceAdminException,
)
from .moodle_exceptions import (
    AccessTokenException,
    UnclassifiedMoodleException,
)
from .orm_exceptions import (
    ForeignKeyViolationException,
    NoEntityFoundException,
    UniqueConstraintViolationException,
)
from .websocket_exceptions import UnexpectedWebsocketException

from .register_exceptions_handlers import register_exceptions_handlers

__all__ = (
    "AccessTokenException",
    "AdminSuicideException",
    "ForeignKeyViolationException",
    "GroupIDMismatchException",
    "NoEntityFoundException",
    "register_exceptions_handlers",
    "SubjectIsOutOfWorkspaceException",
    "UnclassifiedMoodleException",
    "UnexpectedWebsocketException",
    "UniqueConstraintViolationException",
    "UserIsNotWorkspaceAdminException",
)
