"""
User routes — current user profile and admin user management.
"""

import uuid
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import DBDep, CurrentUser, CurrentStudent, AdminUser
from app.schemas import (
    MeResponse,
    UserOut,
    StudentOut,
    StudentUpdate,
    AdminUserOut,
    AdminUserRolesUpdate,
    AdminUserStatusUpdate,
)
from app import crud

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeResponse)
async def get_me(db: DBDep, user: CurrentUser):
    """Return the current user's profile including student/professor info and roles."""
    student = await crud.students.get_by_user_id(db, user.id)
    professor = await crud.professors.get_by_user_id(db, user.id)
    roles = await crud.roles.get_user_roles(db, user.id)

    return MeResponse(
        user=UserOut.model_validate(user),
        student=StudentOut.model_validate(student) if student else None,
        professor=None,  # ProfessorOut omitted from response for students; included if professor
        roles=[r.role for r in roles],
    )


@router.patch("/me", response_model=StudentOut)
async def update_my_profile(
    body: StudentUpdate,
    db: DBDep,
    student: CurrentStudent,
):
    """Update the current student's profile (major)."""
    if body.major is not None:
        student = await crud.students.update_major(db, student, body.major)
        await db.commit()
    return StudentOut.model_validate(student)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(db: DBDep, user: CurrentUser):
    """
    Permanently delete the current user's account and all associated data.
    Cascades to student profile and reviews via DB foreign key constraints.
    """
    await crud.users.delete(db, user)
    await db.commit()


@router.get("/admin/list", response_model=list[AdminUserOut])
async def list_users_for_admin(
    db: DBDep,
    _: AdminUser,
    role: Optional[Literal["admin", "professor", "student"]] = Query(default=None),
    status_filter: Optional[Literal["active", "suspended", "inactive"]] = Query(default=None),
    search: Optional[str] = Query(default=None, min_length=2),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    users = await crud.users.list_for_admin(
        db,
        role=role,
        status=status_filter,
        search=search,
        skip=skip,
        limit=limit,
    )
    return [await _to_admin_user_out(db, u) for u in users]


@router.patch("/admin/{user_id}/roles", response_model=AdminUserOut)
async def update_user_roles(
    user_id: uuid.UUID,
    body: AdminUserRolesUpdate,
    db: DBDep,
    admin: AdminUser,
):
    target = await crud.users.get_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    desired_roles = sorted(set(body.roles))
    current_roles = [r.role for r in await crud.roles.get_user_roles(db, target.id)]

    if admin.id == target.id and "admin" not in desired_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove your own admin role.",
        )

    if "admin" in current_roles and "admin" not in desired_roles:
        admin_count = await crud.roles.count_users_with_role(db, "admin")
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin from the system.",
            )

    role_map = {}
    for role_name in ["admin", "professor", "student"]:
        role_obj = await crud.roles.get_role_by_name(db, role_name)
        if role_obj is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Role '{role_name}' is not configured.",
            )
        role_map[role_name] = role_obj

    for role_name in current_roles:
        if role_name not in desired_roles and role_name in role_map:
            await crud.roles.revoke_role_from_user(db, target.id, role_map[role_name].id)

    for role_name in desired_roles:
        await crud.roles.assign_role_to_user(db, target.id, role_map[role_name].id)

    await db.commit()
    updated = await crud.users.get_by_id(db, target.id)
    return await _to_admin_user_out(db, updated)


@router.patch("/admin/{user_id}/status", response_model=AdminUserOut)
async def update_user_status(
    user_id: uuid.UUID,
    body: AdminUserStatusUpdate,
    db: DBDep,
    admin: AdminUser,
):
    target = await crud.users.get_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if admin.id == target.id and body.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot suspend or deactivate your own account.",
        )

    target = await crud.users.update_status(db, target, body.status)
    await db.commit()
    return await _to_admin_user_out(db, target)


async def _to_admin_user_out(db: DBDep, user) -> AdminUserOut:
    roles = [r.role for r in await crud.roles.get_user_roles(db, user.id)]
    student = await crud.students.get_by_user_id(db, user.id)
    professor = await crud.professors.get_by_user_id(db, user.id)
    professor_name = None
    if professor:
        professor_name = f"{professor.first_name} {professor.last_name}"

    return AdminUserOut(
        id=user.id,
        status=user.status,
        created_at=user.created_at,
        last_login=user.last_login,
        roles=roles,
        student_username=student.username if student else None,
        student_major=student.major if student else None,
        professor_name=professor_name,
    )
