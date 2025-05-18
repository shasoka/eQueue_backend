"""
Пакет, содержащий функции, которые взаимодействуют с REST API еКурсов и
логически связаны с заданиями по предметам.
"""

from .requests import get_tasks_from_course_structure

__all__ = ("get_tasks_from_course_structure",)
