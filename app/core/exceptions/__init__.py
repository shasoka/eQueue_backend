from .business_logic_exceptions import (
    AdminSuicideException,
    GroupIDMismatchException,
    SubmissionForbiddenException,
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
    "SubmissionForbiddenException",
    "SubjectIsOutOfWorkspaceException",
    "UnclassifiedMoodleException",
    "UnexpectedWebsocketException",
    "UniqueConstraintViolationException",
    "UserIsNotWorkspaceAdminException",
)
