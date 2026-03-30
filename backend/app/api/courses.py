"""
Courses, Sections, and Professors routes.
"""

import uuid
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import DBDep, CurrentUserOptional
from app.schemas import (
    CourseOut, CourseOutWithStats,
    SectionOut, SectionOutBrief,
    ProfessorOut, ProfessorOutWithStats,
    SemesterOut,
)
from app import crud

# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

courses_router = APIRouter(prefix="/courses", tags=["courses"])


@courses_router.get("", response_model=list[CourseOut])
async def list_courses(
    db: DBDep,
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, min_length=2),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """List all courses, optionally filtered by department or search query."""
    if search:
        return await crud.courses.search(db, search, skip=skip, limit=limit)
    return await crud.courses.get_all(db, department=department, skip=skip, limit=limit)


@courses_router.get("/departments", response_model=list[str])
async def list_departments(db: DBDep):
    """Return all distinct department codes."""
    return await crud.courses.get_departments(db)


@courses_router.get("/{course_id}", response_model=CourseOutWithStats)
async def get_course(course_id: uuid.UUID, db: DBDep):
    course = await crud.courses.get_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    avg = await crud.reviews.get_average_rating_for_section(db, course_id)  # approximation
    return CourseOutWithStats(**CourseOut.model_validate(course).model_dump(), average_rating=avg)


@courses_router.get("/{course_id}/sections", response_model=list[SectionOut])
async def get_course_sections(
    course_id: uuid.UUID,
    db: DBDep,
    semester_id: Optional[uuid.UUID] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    course = await crud.courses.get_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    sections = await crud.sections.get_by_course(db, course_id, semester_id=semester_id, skip=skip, limit=limit)
    return sections


# ---------------------------------------------------------------------------
# Professors
# ---------------------------------------------------------------------------

professors_router = APIRouter(prefix="/professors", tags=["professors"])


@professors_router.get("", response_model=list[ProfessorOut])
async def list_professors(
    db: DBDep,
    department: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, min_length=2),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    if search:
        return await crud.professors.search(db, search, skip=skip, limit=limit)
    return await crud.professors.get_all(db, department=department, skip=skip, limit=limit)


@professors_router.get("/{professor_id}", response_model=ProfessorOutWithStats)
async def get_professor(professor_id: uuid.UUID, db: DBDep):
    professor = await crud.professors.get_by_id(db, professor_id)
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")
    avg = await crud.reviews.get_average_rating_for_professor(db, professor_id)
    return ProfessorOutWithStats(
        **ProfessorOut.model_validate(professor).model_dump(),
        average_rating=avg,
    )


@professors_router.get("/{professor_id}/sections", response_model=list[SectionOut])
async def get_professor_sections(
    professor_id: uuid.UUID,
    db: DBDep,
    semester_id: Optional[uuid.UUID] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    professor = await crud.professors.get_by_id(db, professor_id)
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")
    return await crud.sections.get_by_professor(
        db, professor_id, semester_id=semester_id, skip=skip, limit=limit
    )

@professors_router.get("/{professor_id}/courses", response_model=list[CourseOut])
async def get_professor_courses(
    professor_id: uuid.UUID,
    db: DBDep,
):
    professor = await crud.professors.get_by_id(db, professor_id)
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")

    return await crud.professors.get_courses_by_professor(db, professor_id)
# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

sections_router = APIRouter(prefix="/sections", tags=["sections"])


@sections_router.get("/{section_id}", response_model=SectionOut)
async def get_section(section_id: uuid.UUID, db: DBDep):
    section = await crud.sections.get_by_id(db, section_id, load_relations=True)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section


# ---------------------------------------------------------------------------
# Semesters
# ---------------------------------------------------------------------------

semesters_router = APIRouter(prefix="/semesters", tags=["semesters"])


@semesters_router.get("", response_model=list[SemesterOut])
async def list_semesters(db: DBDep):
    return await crud.semesters.get_all(db)


@semesters_router.get("/current", response_model=Optional[SemesterOut])
async def get_current_semester(db: DBDep):
    return await crud.semesters.get_current(db)
