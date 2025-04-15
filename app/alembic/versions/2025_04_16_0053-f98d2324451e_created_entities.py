"""Created entities

Revision ID: f98d2324451e
Revises: 
Create Date: 2025-04-16 00:53:22.335284

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f98d2324451e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
        sa.UniqueConstraint("name", name=op.f("uq_groups_name")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("ecourses_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("second_name", sa.String(length=255), nullable=False),
        sa.Column(
            "profile_status",
            sa.String(length=255),
            server_default=sa.text("'Страшно учусь 🥲'"),
            nullable=False,
        ),
        sa.Column("profile_pic_url", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["groups.id"], name=op.f("fk_users_group_id_groups")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("ecourses_id", name=op.f("uq_users_ecourses_id")),
        sa.UniqueConstraint("token", name=op.f("uq_users_token")),
    )
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_workspaces_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspaces")),
        sa.UniqueConstraint(
            "group_id", "name", name=op.f("uq_workspaces_group_id_name")
        ),
    )
    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("ecourses_id", sa.Integer(), nullable=True),
        sa.Column("ecourses_link", sa.String(length=255), nullable=True),
        sa.Column("professor_name", sa.String(length=255), nullable=True),
        sa.Column("professor_contact", sa.String(length=255), nullable=True),
        sa.Column("professor_requirements", sa.Text(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_subjects_workspace_id_workspaces"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
        sa.UniqueConstraint(
            "workspace_id",
            "ecourses_id",
            name=op.f("uq_subjects_workspace_id_ecourses_id"),
        ),
        sa.UniqueConstraint(
            "workspace_id", "name", name=op.f("uq_subjects_workspace_id_name")
        ),
    )
    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column(
            "is_admin",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_workspace_members_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=op.f("fk_workspace_members_workspace_id_workspaces"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workspace_members")),
        sa.UniqueConstraint(
            "user_id",
            "workspace_id",
            name=op.f("uq_workspace_members_user_id_workspace_id"),
        ),
    )
    op.create_table(
        "queues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column(
            "members_can_freeze",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name=op.f("fk_queues_subject_id_subjects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queues")),
        sa.UniqueConstraint("subject_id", name=op.f("uq_queues_subject_id")),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name=op.f("fk_tasks_subject_id_subjects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
        sa.UniqueConstraint(
            "subject_id", "name", name=op.f("uq_tasks_subject_id_name")
        ),
    )
    op.create_table(
        "queue_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("queue_id", sa.Integer(), nullable=False),
        sa.Column(
            "entered_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["queue_id"],
            ["queues.id"],
            name=op.f("fk_queue_members_queue_id_queues"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_queue_members_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_queue_members")),
        sa.UniqueConstraint(
            "user_id",
            "queue_id",
            name=op.f("uq_queue_members_user_id_queue_id"),
        ),
    )
    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_submissions_task_id_tasks"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_submissions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
        sa.UniqueConstraint(
            "user_id", "task_id", name=op.f("uq_submissions_user_id_task_id")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("submissions")
    op.drop_table("queue_members")
    op.drop_table("tasks")
    op.drop_table("queues")
    op.drop_table("workspace_members")
    op.drop_table("subjects")
    op.drop_table("workspaces")
    op.drop_table("users")
    op.drop_table("groups")
