"""Relax legacy violations.category requirement for ORM compatibility.

Revision ID: relax_legacy_violations_category
Revises: reconcile_violations_schema
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "relax_legacy_violations_category"
down_revision: Union[str, Sequence[str], None] = "reconcile_violations_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = {column["name"]: column for column in inspector.get_columns("violations")}
    category = columns.get("category")

    if category is not None:
        # Legacy schema required category, but current ORM no longer writes it.
        # Keep the column for backward compatibility while allowing NULL inserts.
        op.alter_column(
            "violations",
            "category",
            existing_type=sa.String(length=50),
            nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = {column["name"]: column for column in inspector.get_columns("violations")}
    category = columns.get("category")

    if category is not None:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET category = 'other'
                WHERE category IS NULL
                """
            )
        )
        op.alter_column(
            "violations",
            "category",
            existing_type=sa.String(length=50),
            nullable=False,
        )
