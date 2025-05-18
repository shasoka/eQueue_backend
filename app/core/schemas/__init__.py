"""Пакет, содержащий pydantic-схемы для сущностей."""

from typing import Annotated

from pydantic import StringConstraints

__all__ = ("str255",)

# noinspection PyTypeHints
type str255 = Annotated[str, StringConstraints(max_length=255)]
