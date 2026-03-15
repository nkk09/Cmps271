"""
Models package — import all models here so SQLAlchemy's mapper can resolve
all relationships before any session is opened.
"""

from app.models.user import User
from app.models.role import Role, Permission, RolePermission, UserRole
from app.models.professor import Professor
from app.models.student import Student
from app.models.course import Course
from app.models.semester import Semester
from app.models.section import Section
from app.models.review import Review
from app.models.review_interaction import ReviewInteraction
from app.models.violation import Violation
from app.models.otp import OTP

__all__ = [
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Professor",
    "Student",
    "Course",
    "Semester",
    "Section",
    "Review",
    "ReviewInteraction",
    "Violation",
    "OTP",
]