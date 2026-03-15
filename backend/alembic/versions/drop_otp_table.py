"""Compatibility placeholder for historical revision id

Revision ID: drop_otp_table
Revises: create_roles
Create Date: 2026-03-15

This migration is intentionally a no-op so environments that already have
this historical revision recorded in alembic_version can continue upgrading.
"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "drop_otp_table"
down_revision: Union[str, Sequence[str], None] = "create_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
