"""
Student ORM model with anonymous username generation.
"""

import uuid
import random
import secrets
from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


# ---------------------------------------------------------------------------
# Word lists for anonymous username generation
# ---------------------------------------------------------------------------

_ADJECTIVES = [
    "colorful", "bright", "swift", "silent", "bold", "calm", "eager", "fancy",
    "gentle", "happy", "idle", "jolly", "keen", "lively", "mighty", "noble",
    "quick", "radiant", "smart", "true", "vague", "vital", "warm", "young",
    "zesty", "azure", "bronze", "cosmic", "digital", "elegant", "fiery", "golden",
    "honest", "icy", "jazzy", "kind", "lunar", "mystic", "nimble", "orange",
    "prismatic", "quirky", "rosy", "serene", "timely", "urban", "vivid",
]

_NOUNS = [
    "flower", "river", "mountain", "forest", "ocean", "sky", "star", "moon",
    "sun", "wind", "thunder", "crystal", "diamond", "pearl", "butterfly", "eagle",
    "lion", "wolf", "fox", "owl", "panda", "tiger", "dolphin", "whale",
    "rainbow", "cloud", "storm", "sunrise", "sunset", "dawn", "dusk", "flame",
    "frost", "snow", "tree", "garden", "meadow", "canyon", "island", "volcano",
    "glacier", "waterfall", "phoenix", "dragon", "shadow", "breeze", "wave",
    "horizon", "zenith", "nebula", "comet", "asteroid",
]


def _generate_username() -> str:
    """Generate a random anonymous username: AdjectiveNoun1234"""
    adjective = random.choice(_ADJECTIVES).capitalize()
    noun = random.choice(_NOUNS).capitalize()
    number = random.randint(0, 9999)
    return f"{adjective}{noun}{number}"


def generate_unique_username(session: Session) -> str:
    """
    Generate a username that does not already exist in the students table.
    Falls back to appending a hex suffix after 100 failed attempts.
    """
    for _ in range(100):
        username = _generate_username()
        exists = session.query(Student).filter(Student.username == username).first()
        if not exists:
            return username
    return f"{_generate_username()}-{secrets.token_hex(4)}"


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class Student(Base):
    """
    Student profile. Linked 1-to-1 with a User account.
    Username is anonymous (generated, not the student's real name).
    """
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Anonymous display name — never a real name
    username: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)

    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="student")
    review_interactions: Mapped[list["ReviewInteraction"]] = relationship("ReviewInteraction", back_populates="student")
    reported_violations: Mapped[list["Violation"]] = relationship(
        "Violation",
        foreign_keys="Violation.reported_by_student_id",
        back_populates="reported_by_student",
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, username={self.username})>"