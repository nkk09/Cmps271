"""
CRUD package — import all modules here for convenient access.

Usage in routes:
    from app import crud
    user = await crud.users.get_by_email(db, email)
    review = await crud.reviews.create(db, student_id=..., ...)

Or import directly:
    from app.crud import users, reviews
"""

from app.crud import (
    users,
    otps,
    students,
    professors,
    courses,
    semesters,
    sections,
    reviews,
    review_interactions,
    roles,
)

__all__ = [
    "users",
    "otps",
    "students",
    "professors",
    "courses",
    "semesters",
    "sections",
    "reviews",
    "review_interactions",
    "roles",
]
