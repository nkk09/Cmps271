"""
Course and professor discovery endpoints.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.core.session import require_user
from app.models.user import User
from app.models.course import Course
from app.models.professor import Professor
from app.models.course_section import CourseSection
from app.schemas.course import (
    CourseResponse,
    CourseSectionDetailResponse,
    ProfessorResponse,
)

router = APIRouter()


@router.get("/courses", response_model=list[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
    department: str = Query(None),
    search: str = Query(None),
):
    """
    List all courses with optional filtering.
    
    Query parameters:
    - department: Filter by department (e.g., "Computer Science")
    - search: Search by course number or course name
    """
    query = db.query(Course)
    
    if department:
        query = query.filter(Course.department.ilike(f"%{department}%"))
    
    if search:
        query = query.filter(
            or_(
                Course.course_number.ilike(f"%{search}%"),
                Course.course_name.ilike(f"%{search}%"),
            )
        )
    
    courses = query.order_by(Course.course_number).all()
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get a specific course with all its sections."""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.get("/sections/{section_id}", response_model=CourseSectionDetailResponse)
def get_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get a specific course section with course and professor details."""
    section = db.query(CourseSection).filter(CourseSection.id == section_id).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    return section


@router.get("/sections", response_model=list[CourseSectionDetailResponse])
def list_sections(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
    semester: str = Query(None),
    year: int = Query(None),
    professor_id: int = Query(None),
):
    """
    List course sections with optional filtering.
    
    Query parameters:
    - semester: Filter by semester (e.g., "Fall2024")
    - year: Filter by year (e.g., 2024)
    - professor_id: Filter by professor
    """
    query = db.query(CourseSection)
    
    if semester:
        query = query.filter(CourseSection.semester == semester)
    
    if year:
        query = query.filter(CourseSection.year == year)
    
    if professor_id:
        query = query.filter(CourseSection.professor_id == professor_id)
    
    sections = query.order_by(
        CourseSection.semester.desc(),
        CourseSection.year.desc(),
        CourseSection.course_id
    ).all()
    
    return sections


@router.get("/professors", response_model=list[ProfessorResponse])
def list_professors(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
    department: str = Query(None),
    search: str = Query(None),
):
    """
    List all professors with optional filtering.
    
    Query parameters:
    - department: Filter by department
    - search: Search by first name or last name
    """
    query = db.query(Professor).filter(Professor.status == "active")
    
    if department:
        query = query.filter(Professor.department.ilike(f"%{department}%"))
    
    if search:
        query = query.filter(
            or_(
                Professor.first_name.ilike(f"%{search}%"),
                Professor.last_name.ilike(f"%{search}%"),
            )
        )
    
    professors = query.order_by(Professor.last_name, Professor.first_name).all()
    return professors


@router.get("/professors/{professor_id}", response_model=ProfessorResponse)
def get_professor(
    professor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get a specific professor."""
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor not found"
        )
    
    return professor
