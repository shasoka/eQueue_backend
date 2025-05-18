"""
Пакет, содержащий описания ответов эндпоинтов и функцию для генерации
документации.
"""

from .errors_schemas import generate_responses_for_swagger

__all__ = ("generate_responses_for_swagger",)
