"""
Model exports for the application.
"""

from app.models.user import User
from app.models.otp import OTP
from app.models.course import Course
from app.models.professor import Professor
from app.models.course_section import CourseSection
from app.models.review import Review
from app.models.review_interaction import ReviewInteraction
from app.models.moderation_log import ModerationLog

__all__ = [
    "User",
    "OTP",
    "Course",
    "Professor",
    "CourseSection",
    "Review",
    "ReviewInteraction",
    "ModerationLog",
]
