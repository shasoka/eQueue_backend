"""Модуль, реализующий pydantic-схемы для сущности Subject."""

from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "EcoursesSubjectDescription",
    "SubjectCreate",
    "SubjectRead",
    "SubjectUpdate",
)


class SubjectBase(BaseModel):
    """Базовая схема сущности Subject."""

    workspace_id: int
    ecourses_id: Optional[int]
    ecourses_link: Optional[str255]
    professor_name: Optional[str255]
    professor_contact: Optional[str255]
    professor_requirements: Optional[str]
    name: str255


class SubjectCreate(BaseModel):
    """Схема создания сущности Subject."""

    # Поле workspace_id может быть None в случае ручного создания предметов.
    # Если предметы создаются после запроса курсов, то worksapce_id будет
    # иметь числовое значение, равное id рабочего пространства, для которого
    # запрашивались курсы.
    workspace_id: Optional[int]

    ecourses_id: Optional[int]
    ecourses_link: Optional[str255]
    professor_name: Optional[str255]
    professor_contact: Optional[str255]
    professor_requirements: Optional[str]
    name: str255


class SubjectRead(SubjectBase):
    """
    Схема чтения сущности Subject.
    Унаследована от SubjectBase.
    """

    id: int


class EcoursesSubjectDescription(BaseModel):
    """Схема для данных о предмете, приходящих с еКурсов."""

    id: Optional[int]
    shortname: Optional[str255]
    fullname: Optional[str255]
    displayname: Optional[str255]
    lastaccess: Optional[int]
    isfavourite: Optional[bool]
    hidden: Optional[bool]


class SubjectUpdate(BaseModel):
    """Схема обновления сущности Subject."""

    ecourses_link: Optional[str255] = None
    professor_name: Optional[str255] = None
    professor_contact: Optional[str255] = None
    professor_requirements: Optional[str] = None
    name: Optional[str255] = None
