from typing import Optional

from pydantic import BaseModel

from core.schemas import str255

__all__ = (
    "SubjectRead",
    "SubjectCreate",
    "SubjectUpdate",
    "EcoursesSubjectDescription",
)


class SubjectBase(BaseModel):
    workspace_id: int
    ecourses_id: int | None
    ecourses_link: Optional[str255]
    professor_name: Optional[str255]
    professor_contact: Optional[str255]
    professor_requirements: Optional[str255]
    name: str255


class SubjectCreate(BaseModel):
    # Поле workspace_id может быть None в случае ручного создания предметов.
    # Если предметы создаются после запроса курсов, то worksapce_id будет
    # иметь числовое значение, равное id рабочего пространства, для которого
    # запрашивались курсы.
    workspace_id: int | None

    ecourses_id: int | None
    ecourses_link: Optional[str255]
    professor_name: Optional[str255]
    professor_contact: Optional[str255]
    professor_requirements: Optional[str255]
    name: str255


class SubjectRead(SubjectBase):
    id: int


class EcoursesSubjectDescription(BaseModel):
    id: int | None
    shortname: Optional[str255]
    fullname: Optional[str255]
    displayname: Optional[str255]
    lastaccess: int | None
    isfavourite: bool | None
    hidden: bool | None


class SubjectUpdate(BaseModel):
    ecourses_link: Optional[str255] = None
    professor_name: Optional[str255] = None
    professor_contact: Optional[str255] = None
    professor_requirements: Optional[str255] = None
    name: Optional[str255] = None
