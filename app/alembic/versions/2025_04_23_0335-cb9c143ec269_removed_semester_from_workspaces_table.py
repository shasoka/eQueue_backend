"""Removed semester from workspaces table

Revision ID: cb9c143ec269
Revises: 221012bc3cd5
Create Date: 2025-04-23 03:35:57.135941

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cb9c143ec269"
down_revision: Union[str, None] = "221012bc3cd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("workspaces", "semester")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "workspaces",
        sa.Column(
            "semester", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
