"""Seed roles and permissions

Revision ID: create_roles
Revises: seed_courses
Create Date: 2026-02-23

Roles:
  - admin
  - professor
  - student

Permissions and assignments:
  - admin:   full moderation + all view rights
  - student: write/edit/delete own reviews, vote, view everything
  - professor: view own sections and their reviews only
"""

from alembic import op
import sqlalchemy as sa
import uuid

revision = 'create_roles'
down_revision = 'seed_courses'
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# IDs — fixed so downgrade can delete by ID reliably
# ---------------------------------------------------------------------------

# Roles
ROLE_ADMIN      = 'a1000000-0000-0000-0000-000000000001'
ROLE_PROFESSOR  = 'a1000000-0000-0000-0000-000000000002'
ROLE_STUDENT    = 'a1000000-0000-0000-0000-000000000003'

# Permissions
PERM = {
    # --- Review moderation (admin only) ---
    'review:approve':           'b1000000-0000-0000-0000-000000000001',
    'review:reject':            'b1000000-0000-0000-0000-000000000002',
    'review:delete_any':        'b1000000-0000-0000-0000-000000000003',
    'review:view_pending':      'b1000000-0000-0000-0000-000000000004',

    # --- Review authoring (student) ---
    'review:create':            'b1000000-0000-0000-0000-000000000010',
    'review:edit_own':          'b1000000-0000-0000-0000-000000000011',
    'review:delete_own':        'b1000000-0000-0000-0000-000000000012',

    # --- Voting (student) ---
    'review:vote':              'b1000000-0000-0000-0000-000000000020',

    # --- Viewing (student + professor + admin) ---
    'course:view':              'b1000000-0000-0000-0000-000000000030',
    'section:view':             'b1000000-0000-0000-0000-000000000031',
    'professor:view':           'b1000000-0000-0000-0000-000000000032',
    'review:view_approved':     'b1000000-0000-0000-0000-000000000033',

    # --- Professor-specific ---
    'section:view_own':         'b1000000-0000-0000-0000-000000000040',
    'review:view_own_sections': 'b1000000-0000-0000-0000-000000000041',

    # --- User self-management (all roles) ---
    'user:view_self':           'b1000000-0000-0000-0000-000000000050',
    'user:edit_self':           'b1000000-0000-0000-0000-000000000051',
    'user:delete_self':         'b1000000-0000-0000-0000-000000000052',
}

# Role → permission assignments
ROLE_PERMISSIONS = {
    ROLE_ADMIN: [
        # Moderation
        'review:approve',
        'review:reject',
        'review:delete_any',
        'review:view_pending',
        # Viewing (all)
        'course:view',
        'section:view',
        'professor:view',
        'review:view_approved',
        # Self
        'user:view_self',
        'user:edit_self',
        'user:delete_self',
    ],
    ROLE_STUDENT: [
        # Reviews
        'review:create',
        'review:edit_own',
        'review:delete_own',
        # Voting
        'review:vote',
        # Viewing
        'course:view',
        'section:view',
        'professor:view',
        'review:view_approved',
        # Self
        'user:view_self',
        'user:edit_self',
        'user:delete_self',
    ],
    ROLE_PROFESSOR: [
        # Professors can only see their own sections and the reviews on them
        'section:view_own',
        'review:view_own_sections',
        # Self
        'user:view_self',
        'user:edit_self',
        'user:delete_self',
    ],
}


def upgrade() -> None:
    # --- Roles ---
    op.execute(sa.text("INSERT INTO roles (id, role) VALUES ('" + ROLE_ADMIN     + "', 'admin')"))
    op.execute(sa.text("INSERT INTO roles (id, role) VALUES ('" + ROLE_PROFESSOR + "', 'professor')"))
    op.execute(sa.text("INSERT INTO roles (id, role) VALUES ('" + ROLE_STUDENT   + "', 'student')"))

    # --- Permissions ---
    for name, pid in PERM.items():
        op.execute(sa.text("INSERT INTO permissions (id, permission) VALUES ('" + pid + "', '" + name + "')"))

    # --- Role ↔ Permission assignments ---
    for role_id, perm_names in ROLE_PERMISSIONS.items():
        for perm_name in perm_names:
            rp_id = str(uuid.uuid4())
            perm_id = PERM[perm_name]
            op.execute(sa.text(
                "INSERT INTO role_permissions (id, role_id, permission_id) VALUES ('"
                + rp_id + "', '" + role_id + "', '" + perm_id + "')"
            ))


def downgrade() -> None:
    # Delete in FK order: role_permissions → permissions → roles
    role_ids = ", ".join("'" + r + "'" for r in [ROLE_ADMIN, ROLE_PROFESSOR, ROLE_STUDENT])
    perm_ids = ", ".join("'" + p + "'" for p in PERM.values())

    op.execute(sa.text("DELETE FROM role_permissions WHERE role_id IN (" + role_ids + ")"))
    op.execute(sa.text("DELETE FROM permissions WHERE id IN (" + perm_ids + ")"))
    op.execute(sa.text("DELETE FROM roles WHERE id IN (" + role_ids + ")"))