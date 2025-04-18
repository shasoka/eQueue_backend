"""Added groups seeder

Revision ID: 221012bc3cd5
Revises: 222c9248cc16
Create Date: 2025-04-18 21:16:32.552917

"""

from typing import Sequence, Union

import requests
from alembic import op

from core.config import settings


revision: str = "221012bc3cd5"
down_revision: Union[str, None] = "222c9248cc16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _fetch_raw_groups() -> list[dict]:
    response = requests.get(settings.moodle.timetable_url)
    response.raise_for_status()
    raw_data = response.json()

    unique_groups = []
    for group in raw_data:
        base_name = group["name"].split(" (")[0] + " (Глобальная группа)"
        if base_name not in unique_groups:
            unique_groups.append(base_name)
        if group["name"] not in unique_groups:
            unique_groups.append(group["name"])
    return [{"name": group} for group in unique_groups]


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "INSERT INTO groups (name) VALUES "
        + ",".join(f"('{group['name']}')" for group in _fetch_raw_groups())
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
