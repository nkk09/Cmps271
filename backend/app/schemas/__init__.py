"""
Pydantic schemas for the application.
"""

from app.schemas.user import UserResponse, CurrentUserResponse, LoginRequest
from app.schemas.course import (
    CourseResponse,
    CourseSectionDetailResponse,
    CourseSectionResponse,
    ProfessorResponse,
    CourseFilterQuery,
)
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewDetailResponse,
    ReviewListResponse,
    ReviewFilterQuery,
)

__all__ = [
    # User schemas
    "UserResponse",
    "CurrentUserResponse",
    "LoginRequest",
    # Course schemas
    "CourseResponse",
    "CourseSectionDetailResponse",
    "CourseSectionResponse",
    "ProfessorResponse",
    "CourseFilterQuery",
    # Review schemas
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewDetailResponse",
    "ReviewListResponse",
    "ReviewFilterQuery",
]
