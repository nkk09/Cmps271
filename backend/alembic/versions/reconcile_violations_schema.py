"""Reconcile legacy violations table with current ORM schema.

Revision ID: reconcile_violations_schema
Revises: add_user_moderation_columns
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "reconcile_violations_schema"
down_revision: Union[str, Sequence[str], None] = "add_user_moderation_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = _column_names(inspector, "violations")

    if "reported_by_student_id" not in columns:
        op.add_column("violations", sa.Column("reported_by_student_id", sa.UUID(), nullable=True))

    if "assigned_admin_id" not in columns:
        op.add_column("violations", sa.Column("assigned_admin_id", sa.UUID(), nullable=True))

    if "violation_type" not in columns:
        op.add_column(
            "violations",
            sa.Column("violation_type", sa.String(length=40), nullable=False, server_default="other"),
        )
        op.alter_column("violations", "violation_type", server_default=None)

    if "severity" not in columns:
        op.add_column(
            "violations",
            sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        )
        op.alter_column("violations", "severity", server_default=None)

    if "admin_notes" not in columns:
        op.add_column("violations", sa.Column("admin_notes", sa.Text(), nullable=True))

    if "updated_at" not in columns:
        op.add_column("violations", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Refresh after structural changes.
    inspector = sa.inspect(bind)
    columns = _column_names(inspector, "violations")

    if "reported_by_user_id" in columns and "reported_by_student_id" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations AS v
                SET reported_by_student_id = s.id
                FROM students AS s
                WHERE v.reported_by_user_id = s.user_id
                  AND v.reported_by_student_id IS NULL
                """
            )
        )

    if "resolved_by_user_id" in columns and "assigned_admin_id" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET assigned_admin_id = resolved_by_user_id
                WHERE assigned_admin_id IS NULL
                """
            )
        )

    if "category" in columns and "violation_type" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET violation_type = CASE
                    WHEN category IN ('spam', 'harassment', 'hate_speech', 'misinformation', 'personal_data', 'other')
                        THEN category
                    ELSE 'other'
                END
                WHERE violation_type IS NULL OR violation_type = '' OR violation_type = 'other'
                """
            )
        )

    if "created_at" in columns and "updated_at" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET updated_at = COALESCE(updated_at, created_at, NOW())
                WHERE updated_at IS NULL
                """
            )
        )

    # Make sure required defaults are present on existing rows.
    if "violation_type" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET violation_type = 'other'
                WHERE violation_type IS NULL OR violation_type = ''
                """
            )
        )

    if "severity" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET severity = 'medium'
                WHERE severity IS NULL OR severity = ''
                """
            )
        )

    if "status" in columns:
        op.execute(
            sa.text(
                """
                UPDATE violations
                SET status = 'open'
                WHERE status IS NULL OR status = ''
                """
            )
        )

        # Repair legacy status constraint if it does not include the current in_review state.
        check_constraints = inspector.get_check_constraints("violations")
        for constraint in check_constraints:
            if constraint["name"] == "ck_violation_status":
                if "in_review" not in constraint.get("sqltext", ""):
                    op.drop_constraint("ck_violation_status", "violations", type_="check")
                    op.create_check_constraint(
                        "ck_violation_status",
                        "violations",
                        "status IN ('open', 'in_review', 'resolved', 'dismissed')",
                    )
                break

    # Enforce non-null updated_at to match ORM.
    if "updated_at" in columns:
        op.alter_column("violations", "updated_at", existing_type=sa.DateTime(), nullable=False)

    inspector = sa.inspect(bind)
    index_names = _index_names(inspector, "violations")

    if "ix_violations_reported_by_student_id" not in index_names and "reported_by_student_id" in columns:
        op.create_index("ix_violations_reported_by_student_id", "violations", ["reported_by_student_id"], unique=False)

    if "ix_violations_assigned_admin_id" not in index_names and "assigned_admin_id" in columns:
        op.create_index("ix_violations_assigned_admin_id", "violations", ["assigned_admin_id"], unique=False)

    if "ix_violations_status" not in index_names and "status" in columns:
        op.create_index("ix_violations_status", "violations", ["status"], unique=False)

    if "ix_violations_created_at" not in index_names and "created_at" in columns:
        op.create_index("ix_violations_created_at", "violations", ["created_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("violations"):
        return

    columns = _column_names(inspector, "violations")
    index_names = _index_names(inspector, "violations")

    if "ix_violations_assigned_admin_id" in index_names:
        op.drop_index("ix_violations_assigned_admin_id", table_name="violations")

    if "ix_violations_reported_by_student_id" in index_names:
        op.drop_index("ix_violations_reported_by_student_id", table_name="violations")

    if "updated_at" in columns:
        op.drop_column("violations", "updated_at")

    if "admin_notes" in columns:
        op.drop_column("violations", "admin_notes")

    if "severity" in columns:
        op.drop_column("violations", "severity")

    if "violation_type" in columns:
        op.drop_column("violations", "violation_type")

    if "assigned_admin_id" in columns:
        op.drop_column("violations", "assigned_admin_id")

    if "reported_by_student_id" in columns:
        op.drop_column("violations", "reported_by_student_id")
