"""Fix violation status check constraint to allow in_review.

Revision ID: fix_violation_status_constraint
Revises: reconcile_violations_schema
Create Date: 2026-04-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fix_violation_status_constraint"
down_revision: Union[str, Sequence[str], None] = "reconcile_violations_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    check_constraints = inspector.get_check_constraints("violations")
    if any(constraint["name"] == "ck_violation_status" for constraint in check_constraints):
        op.drop_constraint("ck_violation_status", "violations", type_="check")

    op.create_check_constraint(
        "ck_violation_status",
        "violations",
        "status IN ('open', 'in_review', 'resolved', 'dismissed')",
    )

    op.execute(
        sa.text(
            """
            UPDATE violations
            SET status = 'open'
            WHERE status IS NULL
               OR status = ''
               OR status NOT IN ('open', 'in_review', 'resolved', 'dismissed')
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint("ck_violation_status", "violations", type_="check")
    op.create_check_constraint(
        "ck_violation_status",
        "violations",
        "status IN ('open', 'resolved', 'dismissed')",
    )
