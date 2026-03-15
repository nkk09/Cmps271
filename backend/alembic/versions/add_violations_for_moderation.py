"""Add violations table for admin moderation

Revision ID: add_violations
Revises: create_roles
Create Date: 2026-03-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_violations"
down_revision: Union[str, Sequence[str], None] = "drop_otp_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("violations"):
        return

    op.create_table(
        "violations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("review_id", sa.UUID(), nullable=False),
        sa.Column("reported_by_student_id", sa.UUID(), nullable=True),
        sa.Column("assigned_admin_id", sa.UUID(), nullable=True),
        sa.Column("violation_type", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "violation_type IN ('spam', 'harassment', 'hate_speech', 'misinformation', 'personal_data', 'other')",
            name="ck_violation_type",
        ),
        sa.CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_violation_severity",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'in_review', 'resolved', 'dismissed')",
            name="ck_violation_status",
        ),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reported_by_student_id"], ["students.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("review_id", "reported_by_student_id", name="uq_violation_per_reporter_review"),
    )

    op.create_index(op.f("ix_violations_review_id"), "violations", ["review_id"], unique=False)
    op.create_index(op.f("ix_violations_reported_by_student_id"), "violations", ["reported_by_student_id"], unique=False)
    op.create_index(op.f("ix_violations_assigned_admin_id"), "violations", ["assigned_admin_id"], unique=False)
    op.create_index(op.f("ix_violations_status"), "violations", ["status"], unique=False)
    op.create_index(op.f("ix_violations_created_at"), "violations", ["created_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("violations"):
        return

    op.drop_index(op.f("ix_violations_created_at"), table_name="violations")
    op.drop_index(op.f("ix_violations_status"), table_name="violations")
    op.drop_index(op.f("ix_violations_assigned_admin_id"), table_name="violations")
    op.drop_index(op.f("ix_violations_reported_by_student_id"), table_name="violations")
    op.drop_index(op.f("ix_violations_review_id"), table_name="violations")
    op.drop_table("violations")
