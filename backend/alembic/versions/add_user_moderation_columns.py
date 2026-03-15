"""Add user moderation columns

Revision ID: add_user_moderation_columns
Revises: add_violations
Create Date: 2026-03-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_user_moderation_columns"
down_revision: Union[str, Sequence[str], None] = "add_violations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "is_blocked" not in columns:
        op.add_column(
            "users",
            sa.Column("is_blocked", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        op.alter_column("users", "is_blocked", server_default=None)

    if "muted_until" not in columns:
        op.add_column("users", sa.Column("muted_until", sa.DateTime(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "muted_until" in columns:
        op.drop_column("users", "muted_until")

    if "is_blocked" in columns:
        op.drop_column("users", "is_blocked")
