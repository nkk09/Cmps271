"""
User routes — current user profile.
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies import DBDep, CurrentUser, CurrentStudent
from app.schemas import MeResponse, UserOut, StudentOut, StudentUpdate
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
