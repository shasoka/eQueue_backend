"""
Пакет, содержащий функции, которые взаимодействуют с REST API еКурсов и
логически связаны с авторизацией пользователей.
"""

from .requests import (
    auth_by_moodle_credentials,
    check_access_token_persistence,
    get_moodle_user_info,
)
from .oauth2 import get_current_user

__all__ = (
    "auth_by_moodle_credentials",
    "check_access_token_persistence",
    "get_current_user",
    "get_moodle_user_info",
)
