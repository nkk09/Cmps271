"""Relax legacy violations.reason requirement for ORM compatibility.

Revision ID: relax_legacy_violations_reason
Revises: relax_legacy_violations_category
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "relax_legacy_violations_reason"
down_revision: Union[str, Sequence[str], None] = "relax_legacy_violations_category"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = {column["name"]: column for column in inspector.get_columns("violations")}
    reason = columns.get("reason")

    if reason is not None:
        op.alter_column(
            "violations",
            "reason",
            existing_type=sa.Text(),
            nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = {column["name"]: column for column in inspector.get_columns("violations")}
    reason = columns.get("reason")

    if reason is not None:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET reason = ''
                WHERE reason IS NULL
                """
            )
        )
        op.alter_column(
            "violations",
            "reason",
            existing_type=sa.Text(),
            nullable=False,
        )
