from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
    TIMESTAMP,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint

from .base import Base


class User(Base):

    # --- Поля ---

    # Токен еКурсов
    access_token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # ID пользователя на еКурсах
    ecourses_id: Mapped[int] = mapped_column(
        nullable=False,
        unique=True,
    )

    # ID группы, к которой прикреплен пользователь
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        nullable=True,
    )

    # Имя пользователя
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Фамилия пользователя
    second_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Статус профиля пользователя (внутри eQueue)
    profile_status_default_val: str = "'Страшно учусь 🥲'"
    profile_status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default=profile_status_default_val,
        server_default=text(profile_status_default_val),
    )

    # Ссылка на фото профиля
    profile_pic_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Дата и время срздания профиля (внутри eQueue)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    # Дата и время обновления профиля (внутри eQueue)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )

    # --- Связи ---

    # One-to-many
    # Одна и та же группа у многих пользователей
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="users",
    )

    # Many-to-one
    # Один и тот же пользователь у многих рабочих пространств
    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="user",
    )

    # Many-to-one
    # Один и тот же пользователь у многих сданных заданий
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="user",
    )

    # Many-to-one
    # Один и тот же пользователь во многих очередях
    queue_memberships: Mapped[list["QueueMember"]] = relationship(
        "QueueMember",
        back_populates="user",
    )


class Group(Base):

    # --- Поля ---

    # Наименование группы
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # --- Связи ---

    # Many-to-one
    # Много пользователей в одной и той же группе
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="group",
    )

    # Many-to-one
    # Много рабочих пространств с одной и той же группой
    workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="group",
    )


class Workspace(Base):

    # --- Поля ---

    # ID группы
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        nullable=False,
    )

    # Название рабочего пространства
    # unique = False, т.к. может существовать два рабочих пространства с
    # одинаковыми наименованиями, но с разными group_id
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Семестр
    semester: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Дата и время срздания рабочего пространства
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    # Дата и время обновления рабочего пространства
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )

    # --- Связи ---

    # One-to-many
    # Одна и та же группа у многих рабочих пространств
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="workspaces",
    )

    # Many-to-one
    # Много пользователей в одном и том же рабочем пространстве
    members: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="workspace",
    )

    # Many-to-one
    # Много предметов в одном и том же рабочем пространстве
    subjects: Mapped[list["Subject"]] = relationship(
        "Subject",
        back_populates="workspace",
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Уникальность названия рабочего пространства в рамках одной группы
        UniqueConstraint(
            "group_id",
            "name",
        ),
    )


class WorkspaceMember(Base):

    # --- Поля ---

    # ID пользователя
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # ID рабочего пространства
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id"),
        nullable=False,
    )

    # Флаг определяющий является ли член пространства его администратором
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    # Статус члена рабочего пространства (pending, approved, rejected)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="'pending'",
        server_default=text("'pending'"),
    )

    # Дата вступления в рабочее пространство
    # При выходе запись об этом члене удаляется, при повторном вступлении -
    # появляется снова
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    # --- Связи ---

    # One-to-many
    # Один пользователь может являться членом многих рабочих пространств
    user: Mapped["User"] = relationship(
        "User",
        back_populates="workspace_memberships",
    )

    # One-to-many
    # Одно рабочее пространство может иметь много членов
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="members",
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Ограничение уникальности пользователя в рабочем пространстве
        UniqueConstraint(
            "user_id",
            "workspace_id",
        ),
    )


class Subject(Base):

    # --- Поля ---

    # ID рабочего пространства
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id"),
        nullable=False,
    )

    # ID предмета на еКурсах
    ecourses_id: Mapped[int] = mapped_column(
        nullable=True,
    )

    # Ссылка на предмет на еКурсах
    ecourses_link: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Имя преподавателя
    professor_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Контакт преподавателя
    professor_contact: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # Требования преподавателя к сдаче работ
    professor_requirements: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    # Название предмета
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # --- Связи ----

    # One-to-many
    # Одно рабочее пространство может иметь много предметов
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="subjects",
    )

    # Many-to-one
    # Много заданий в одном и том же предмете
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="subject",
    )

    # One-to-one
    # Один предмет может иметь одну очередь для сдачи
    queue: Mapped["Queue"] = relationship(
        "Queue",
        back_populates="subject",
        uselist=False,  # One-to-one
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Уникальность имени предмета в рамках одного рабочего пространства
        UniqueConstraint(
            "workspace_id",
            "name",
        ),
        # Уникальность ecourses_id в рамках одного рабочего пространства
        # Только если ecourses_id НЕ NULL (частично индексируемое ограничение)
        UniqueConstraint(
            "workspace_id",
            "ecourses_id",
        ),
    )


class Queue(Base):

    # --- Поля ---

    # ID предмета
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
        unique=True,  # uq_queue_sid
    )

    # Флаг определяющий могут ли пользователи в очереди "замораживать" свое
    # положение в ней
    members_can_freeze: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    # --- Связи ---

    # One-to-many
    # Один предмет может иметь одну очередь
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="queue",
    )

    # Many-to-one
    # Много членов могут находится в одной очереди
    members: Mapped[list["QueueMember"]] = relationship(
        "QueueMember",
        back_populates="queue",
    )


class QueueMember(Base):

    # --- Поля ---

    # ID пользователя
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # ID очереди
    queue_id: Mapped[int] = mapped_column(
        ForeignKey("queues.id"),
        nullable=False,
    )

    # Время вступления в очередь
    entered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    # Позиция в очереди
    position: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Статус члена в очереди. Значения: 'active', 'frozen'.
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="'active'",
        server_default=text("'active'"),
    )

    # --- Связи ---

    # One-to-many
    # Один пользователь может являться членом многих очередей
    user: Mapped["User"] = relationship(
        "User",
        back_populates="queue_memberships",
    )

    # One-to-many
    # В одной очереди может быть много членов
    queue: Mapped["Queue"] = relationship(
        "Queue",
        back_populates="members",
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Ограничение в одну попытку для вступления в очередь
        # Один и тот же пользователь не может вступить в очередь дважды
        UniqueConstraint(
            "user_id",
            "queue_id",
        ),
    )


class Task(Base):

    # --- Поля ---

    # ID предмета
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
    )

    # Наименование задания
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Ссылка на задание на еКурсах
    url: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    # --- Связи ---

    # One-to-many
    # Один и тот же предмет может иметь много различных заданий
    subject: Mapped["Subject"] = relationship(
        "Subject",
        back_populates="tasks",
    )

    # Many-to-one
    # Одно задание может иметь много попыток сдачи разными пользователями
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="task",
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Уникальность названия задания в рамках одного предмета
        UniqueConstraint(
            "subject_id",
            "name",
        ),
    )


class Submission(Base):

    # --- Поля ---

    # ID задания
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False,
    )

    # ID пользователя
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # Время сдачи задания
    submitted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    # --- Связи ---

    # One-to-many
    # Одно задание может иметь много попыток сдачи разными пользователями
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="submissions",
    )

    # One-to-many
    # Один пользователь может иметь много попыток сдачи различных заданий
    user: Mapped["User"] = relationship(
        "User",
        back_populates="submissions",
    )

    # --- Ограничения уникальности ---

    __table_args__ = (
        # Ограничение в одну попытку для сдачи одной работы одним
        # пользователем
        UniqueConstraint(
            "user_id",
            "task_id",
        ),
    )
