"""Renamed users.token -> users.access_token

Revision ID: 222c9248cc16
Revises: f98d2324451e
Create Date: 2025-04-18 19:16:06.839590

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "222c9248cc16"
down_revision: Union[str, None] = "f98d2324451e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("access_token", sa.String(length=255), nullable=False),
    )
    op.drop_constraint("uq_users_token", "users", type_="unique")
    op.create_unique_constraint(
        op.f("uq_users_access_token"), "users", ["access_token"]
    )
    op.drop_column("users", "token")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "token",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_constraint(op.f("uq_users_access_token"), "users", type_="unique")
    op.create_unique_constraint("uq_users_token", "users", ["token"])
    op.drop_column("users", "access_token")
