from pydantic import BaseModel


__all__ = ("SubjectRead", "SubjectCreate")


class SubjectBase(BaseModel):
    workspace_id: int
    ecourses_id: int | None
    ecourses_link: str | None
    professor_name: str | None
    professor_contact: str | None
    professor_requirements: str | None
    name: str


class SubjectCreate(BaseModel):
    workspace_id: int
    ecourses_id: int | None = None
    ecourses_link: str | None = None
    professor_name: str | None = None
    professor_contact: str | None = None
    professor_requirements: str | None = None
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
