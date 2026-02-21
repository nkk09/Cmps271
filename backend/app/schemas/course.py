"""
Pydantic schemas for courses, professors, and sections.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProfessorResponse(BaseModel):
    """Professor response - public info only."""
    id: int
    first_name: str
    last_name: str
    department: Optional[str]
    
    class Config:
        from_attributes = True


class CourseSectionResponse(BaseModel):
    """Course section details."""
    id: int
    section_number: str
    semester: str
    year: int
    time: Optional[str]
    location: Optional[str]
    professor: ProfessorResponse
    
    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    """Course response with sections."""
    id: int
    course_number: str
    course_name: str
    department: str
    credit_hours: Optional[int]
    description: Optional[str]
    sections: list[CourseSectionResponse] = []
    
    class Config:
        from_attributes = True


class CourseSectionDetailResponse(BaseModel):
    """Course section with course details."""
    id: int
    section_number: str
    semester: str
    year: int
    time: Optional[str]
    location: Optional[str]
    course: CourseResponse
    professor: ProfessorResponse
    
    class Config:
        from_attributes = True


class CourseFilterQuery(BaseModel):
    """Query parameters for filtering courses."""
    department: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    professor_name: Optional[str] = None
