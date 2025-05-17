"""Added ondelete behaviour

Revision ID: 9c63893fff56
Revises: cb9c143ec269
Create Date: 2025-04-23 20:29:50.527741

"""

from typing import Sequence, Union

from alembic import op


revision: str = "9c63893fff56"
down_revision: Union[str, None] = "cb9c143ec269"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        "fk_queue_members_user_id_users", "queue_members", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_queue_members_queue_id_queues", "queue_members", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_queue_members_queue_id_queues"),
        "queue_members",
        "queues",
        ["queue_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_queue_members_user_id_users"),
        "queue_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_queues_subject_id_subjects", "queues", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_queues_subject_id_subjects"),
        "queues",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_subjects_workspace_id_workspaces", "subjects", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_subjects_workspace_id_workspaces"),
        "subjects",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_submissions_user_id_users", "submissions", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_submissions_task_id_tasks", "submissions", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_submissions_user_id_users"),
        "submissions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_submissions_task_id_tasks"),
        "submissions",
        "tasks",
        ["task_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_tasks_subject_id_subjects", "tasks", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_tasks_subject_id_subjects"),
        "tasks",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("fk_users_group_id_groups", "users", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_users_group_id_groups"),
        "users",
        "groups",
        ["group_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(
        "fk_workspace_members_workspace_id_workspaces",
        "workspace_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_workspace_members_user_id_users",
        "workspace_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_workspace_members_user_id_users"),
        "workspace_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_workspace_members_workspace_id_workspaces"),
        "workspace_members",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_workspaces_group_id_groups", "workspaces", type_="foreignkey"
    )
    op.create_foreign_key(
        op.f("fk_workspaces_group_id_groups"),
        "workspaces",
        "groups",
        ["group_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_workspaces_group_id_groups"), "workspaces", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_workspaces_group_id_groups",
        "workspaces",
        "groups",
        ["group_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_workspace_members_workspace_id_workspaces"),
        "workspace_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_workspace_members_user_id_users"),
        "workspace_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_workspace_members_user_id_users",
        "workspace_members",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_workspace_members_workspace_id_workspaces",
        "workspace_members",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_users_group_id_groups"), "users", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_users_group_id_groups", "users", "groups", ["group_id"], ["id"]
    )
    op.drop_constraint(
        op.f("fk_tasks_subject_id_subjects"), "tasks", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_tasks_subject_id_subjects",
        "tasks",
        "subjects",
        ["subject_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_submissions_task_id_tasks"), "submissions", type_="foreignkey"
    )
    op.drop_constraint(
        op.f("fk_submissions_user_id_users"), "submissions", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_submissions_task_id_tasks",
        "submissions",
        "tasks",
        ["task_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_submissions_user_id_users",
        "submissions",
        "users",
        ["user_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_subjects_workspace_id_workspaces"),
        "subjects",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_subjects_workspace_id_workspaces",
        "subjects",
        "workspaces",
        ["workspace_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_queues_subject_id_subjects"), "queues", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_queues_subject_id_subjects",
        "queues",
        "subjects",
        ["subject_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_queue_members_user_id_users"),
        "queue_members",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_queue_members_queue_id_queues"),
        "queue_members",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_queue_members_queue_id_queues",
        "queue_members",
        "queues",
        ["queue_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_queue_members_user_id_users",
        "queue_members",
        "users",
        ["user_id"],
        ["id"],
    )
