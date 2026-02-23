"""
Pydantic schemas for request validation and response serialization.
"""

import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserOut(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    user: UserOut
    student: Optional["StudentOut"] = None
    professor: Optional["ProfessorOut"] = None
    roles: list[str] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentOut(BaseModel):
    id: uuid.UUID
    username: str
    major: Optional[str]

    model_config = {"from_attributes": True}


class StudentUpdate(BaseModel):
    major: Optional[str] = None


# ---------------------------------------------------------------------------
# Professor
# ---------------------------------------------------------------------------

class ProfessorOut(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    department: Optional[str]

    model_config = {"from_attributes": True}


class ProfessorOutWithStats(ProfessorOut):
    average_rating: Optional[float] = None


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class CourseOut(BaseModel):
    id: uuid.UUID
    code: str
    title: str
    department: str
    description: Optional[str]
    attributes: Optional[list[str]]

    model_config = {"from_attributes": True}


class CourseOutWithStats(CourseOut):
    average_rating: Optional[float] = None


# ---------------------------------------------------------------------------
# Semester
# ---------------------------------------------------------------------------

class SemesterOut(BaseModel):
    id: uuid.UUID
    name: str
    starts_on: datetime
    ends_on: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------

class SectionOut(BaseModel):
    id: uuid.UUID
    section_number: str
    credits: Optional[int]
    time: Optional[str]
    course: CourseOut
    professor: ProfessorOut
    semester: SemesterOut

    model_config = {"from_attributes": True}


class SectionOutBrief(BaseModel):
    """Lighter version used when sections are nested under course/professor."""
    id: uuid.UUID
    section_number: str
    credits: Optional[int]
    time: Optional[str]
    semester: SemesterOut

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class ReviewCreate(BaseModel):
    content: str = Field(min_length=20, max_length=5000)
    rating: float = Field(ge=1.0, le=5.0)


class ReviewUpdate(BaseModel):
    content: Optional[str] = Field(default=None, min_length=20, max_length=5000)
    rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class ReviewOut(BaseModel):
    id: uuid.UUID
    content: str
    rating: float
    status: str
    likes_count: int
    dislikes_count: int
    created_at: datetime
    updated_at: datetime
    student: StudentOut
    # The caller's interaction with this review (if authenticated student)
    my_interaction: Optional[Literal["like", "dislike"]] = None

    model_config = {"from_attributes": True}


class ReviewStatusUpdate(BaseModel):
    status: Literal["approved", "rejected"]


# ---------------------------------------------------------------------------
# Review Interaction
# ---------------------------------------------------------------------------

class InteractionResponse(BaseModel):
    review_id: uuid.UUID
    interaction_type: Literal["like", "dislike"]
    likes_count: int
    dislikes_count: int


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    total: Optional[int] = None
    skip: int
    limit: int
    items: list


# Resolve forward references
MeResponse.model_rebuild()
