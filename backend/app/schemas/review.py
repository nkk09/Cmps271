"""
Pydantic schemas for reviews.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    """Create a new review."""
    course_id: int
    professor_id: int
    section_id: Optional[int] = None
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    rating: float = Field(..., ge=1.0, le=5.0)
    attributes: Optional[str] = None  # comma-separated tags


class ReviewUpdate(BaseModel):
    """Update an existing review."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    attributes: Optional[str] = None


class ReviewResponse(BaseModel):
    """Public review response - anonymized."""
    id: int
    title: str
    content: str
    rating: float
    attributes: Optional[str]
    reviewer_username: str  # Anonymous username only
    course_number: str
    professor_name: str
    likes_count: int
    dislikes_count: int
    net_rating: int  # likes - dislikes
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReviewDetailResponse(ReviewResponse):
    """Detailed review response with more info."""
    status: str  # approval status
    semester: Optional[str]
    year: Optional[int]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Review list with pagination."""
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int


class ReviewFilterQuery(BaseModel):
    """Query parameters for filtering reviews."""
    course_id: Optional[int] = None
    professor_id: Optional[int] = None
    section_id: Optional[int] = None
    semester: Optional[str] = None
    rating_min: Optional[float] = Field(None, ge=1.0, le=5.0)
    rating_max: Optional[float] = Field(None, ge=1.0, le=5.0)
    sort_by: Optional[str] = Field("created_at", pattern="^(created_at|rating|net_rating)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
