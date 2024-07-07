from sqlalchemy import String, TIMESTAMP, func, ForeignKey, ARRAY, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    moodle_token: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    ecourses_user_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    assigned_group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    second_name: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(100), default="Привет! Я использую eQueue! 🎫")
    talon: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    user_picture_url: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user"
    )
    assigned_group: Mapped["Group"] = relationship(
        "Group",
        back_populates="users"
    )
    submissions: Mapped[list["UserSubmission"]] = relationship(
        "UserSubmission",
        back_populates="user"
    )


class Achievement(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="achievement"
    )


class UserAchievement(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, unique=True)
    achievement_id: Mapped[int] = mapped_column(ForeignKey('achievements.id'), nullable=False, unique=True)

    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement",
        back_populates="user_achievements"
    )


class Group(Base):
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="assigned_group"
    )
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="group"
    )


class Workspace(Base):
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=False, unique=True)
    chief_id: Mapped[int] = mapped_column(nullable=False)
    semester: Mapped[int] = mapped_column(default=1, nullable=False)
    about: Mapped[str] = mapped_column(nullable=False, default='Рабочее пространство группы %s')

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="workspace"
    )
    subjects: Mapped[list["WorkspaceSubject"]] = relationship(
        "WorkspaceSubject",
        back_populates="workspace"
    )
    submissions: Mapped[list["UserSubmission"]] = relationship(
        "UserSubmission",
        back_populates="workspace"
    )


class Subject(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    workspace_subjects: Mapped[list["WorkspaceSubject"]] = relationship(
        "WorkspaceSubject",
        back_populates="subject"
    )
    submissions: Mapped[list["UserSubmission"]] = relationship(
        "UserSubmission",
        back_populates="subject"
    )


class WorkspaceSubject(Base):
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspaces.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    scoped_name: Mapped[str] = mapped_column(String(50), default=None)
    professor: Mapped[str] = mapped_column(String(255), default=None)
    professor_contact: Mapped[str] = mapped_column(default=None)
    requirements: Mapped[str] = mapped_column(String(255), default=None)
    additional_fields: Mapped[dict] = mapped_column(JSONB, default={})
    queue: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="subjects"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="workspace_subjects"
    )


class UserSubmission(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspaces.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    submitted_works: Mapped[int] = mapped_column(default=0, nullable=False)
    total_required_works: Mapped[int] = mapped_column(default=0, nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="submissions"
    )
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="submissions"
    )
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="submissions"
    )