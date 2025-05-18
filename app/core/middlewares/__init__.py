"""
Пакет, содержащий функцию регистрации middlewares в FastAPI-приложении.
Также содержит вложенный пакет logs, содержащий функцию создания логгера.
"""

from .register_middlewares import register_middlewares

__all__ = ("register_middlewares",)
