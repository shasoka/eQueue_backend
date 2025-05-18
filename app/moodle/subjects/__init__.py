"""
Пакет, содержащий функции, которые взаимодействуют с REST API еКурсов и
логически связаны с предметами.
"""

from .requests import get_user_enrolled_courses

__all__ = ("get_user_enrolled_courses",)
