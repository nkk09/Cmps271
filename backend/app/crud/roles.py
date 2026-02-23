"""
CRUD operations for Role, Permission, UserRole, RolePermission models.
Roles and permissions are mostly seeded at startup.
Runtime operations are primarily assigning/revoking roles from users.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role, Permission, RolePermission, UserRole


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.id == role_id))
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.role == name))
    return result.scalar_one_or_none()


async def get_all_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(select(Role).order_by(Role.role))
    return list(result.scalars().all())


async def create_role(db: AsyncSession, name: str) -> Role:
    role = Role(role=name)
    db.add(role)
    await db.flush()
    return role


async def delete_role(db: AsyncSession, role: Role) -> None:
    await db.delete(role)
    await db.flush()


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

async def get_permission_by_name(db: AsyncSession, name: str) -> Optional[Permission]:
    result = await db.execute(select(Permission).where(Permission.permission == name))
    return result.scalar_one_or_none()


async def create_permission(db: AsyncSession, name: str) -> Permission:
    permission = Permission(permission=name)
    db.add(permission)
    await db.flush()
    return permission


# ---------------------------------------------------------------------------
# Role ↔ Permission
# ---------------------------------------------------------------------------

async def assign_permission_to_role(
    db: AsyncSession,
    role: Role,
    permission: Permission,
) -> RolePermission:
    rp = RolePermission(role_id=role.id, permission_id=permission.id)
    db.add(rp)
    await db.flush()
    return rp


async def revoke_permission_from_role(
    db: AsyncSession,
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )
    rp = result.scalar_one_or_none()
    if rp is None:
        return False
    await db.delete(rp)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# User ↔ Role
# ---------------------------------------------------------------------------

async def get_user_roles(db: AsyncSession, user_id: uuid.UUID) -> list[Role]:
    """Return all Role objects assigned to a user."""
    result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .order_by(Role.role)
    )
    return list(result.scalars().all())


async def get_user_permissions(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    """Return a flat list of permission strings for a user (across all their roles)."""
    result = await db.execute(
        select(Permission.permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
        .distinct()
    )
    return list(result.scalars().all())


async def assign_role_to_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> UserRole:
    # Check if already assigned
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    await db.flush()
    return user_role


async def revoke_role_from_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    role_id: uuid.UUID,
) -> bool:
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
    )
    user_role = result.scalar_one_or_none()
    if user_role is None:
        return False
    await db.delete(user_role)
    await db.flush()
    return True


async def user_has_permission(
    db: AsyncSession,
    user_id: uuid.UUID,
    permission: str,
) -> bool:
    """Quick check: does this user have a specific permission?"""
    permissions = await get_user_permissions(db, user_id)
    return permission in permissions
