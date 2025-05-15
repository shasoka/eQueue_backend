from pydantic import BaseModel


__all__ = (
    "SubjectRead",
    "SubjectCreate",
    "SubjectUpdate",
    "EcoursesSubjectDescription",
)


class SubjectBase(BaseModel):
    workspace_id: int
    ecourses_id: int | None
    ecourses_link: str | None
    professor_name: str | None
    professor_contact: str | None
    professor_requirements: str | None
    name: str


class SubjectCreate(BaseModel):
    # Поле workspace_id может быть None в случае ручного создания предметов.
    # Если предметы создаются после запроса курсов, то worksapce_id будет
    # иметь числовое значение, равное id рабочего пространства, для которого
    # запрашивались курсы.
    workspace_id: int | None

    ecourses_id: int | None
    ecourses_link: str | None
    professor_name: str | None
    professor_contact: str | None
    professor_requirements: str | None
    name: str


class SubjectRead(SubjectBase):
    id: int


class EcoursesSubjectDescription(BaseModel):
    id: int | None
    shortname: str | None
    fullname: str | None
    displayname: str | None
    lastaccess: int | None
    isfavourite: bool | None
    hidden: bool | None


class SubjectUpdate(BaseModel):
    ecourses_link: str | None = None
    professor_name: str | None = None
    professor_contact: str | None = None
    professor_requirements: str | None = None
    name: str | None = None
