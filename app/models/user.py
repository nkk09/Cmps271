"""
User ORM model with anonymous username generation.
"""

from datetime import datetime
from typing import Optional
import secrets
import random
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


# Word lists for pseudorandom username generation
ADJECTIVES = [
    "colorful", "bright", "swift", "silent", "bold", "calm", "eager", "fancy",
    "gentle", "happy", "idle", "jolly", "keen", "lively", "mighty", "noble",
    "quick", "radiant", "smart", "true", "vague", "vital", "warm", "young",
    "zesty", "azure", "bronze", "cosmic", "digital", "elegant", "fiery", "golden",
    "honest", "icy", "jazzy", "kind", "lunar", "mystic", "nimble", "orange",
    "prismatic", "quarky", "rosy", "serene", "swift", "timely", "urban", "vivid"
]

NOUNS = [
    "flower", "river", "mountain", "forest", "ocean", "sky", "star", "moon",
    "sun", "wind", "thunder", "crystal", "diamond", "pearl", "butterfly", "eagle",
    "lion", "wolf", "fox", "owl", "panda", "tiger", "dolphin", "whale",
    "rainbow", "cloud", "storm", "sunrise", "sunset", "dawn", "dusk", "flame",
    "frost", "snow", "tree", "garden", "meadow", "canyon", "island", "volcano",
    "glacier", "waterfall", "phoenix", "dragon", "unicorn", "griffin", "shadow",
    "light", "breeze", "wave", "horizon", "zenith", "nebula", "comet", "asteroid"
]


def generate_username() -> str:
    """
    Generate a pseudorandom anonymous username in format: AdjectiveNounNumber
    Examples: ColorfulFlowerNumber, BrightStarNumber, SwiftEagleNumber123
    """
    adjective = random.choice(ADJECTIVES).capitalize()
    noun = random.choice(NOUNS).capitalize()
    number = random.randint(0, 9999)
    return f"{adjective}{noun}{number}"


def generate_unique_username(session) -> str:
    """
    Generate a unique username that doesn't already exist in database.
    """
    max_attempts = 100
    for _ in range(max_attempts):
        username = generate_username()
        # Check if username already exists
        existing = session.query(User).filter(User.username == username).first()
        if not existing:
            return username
    
    # Fallback: add random suffix if all attempts fail
    return f"{generate_username()}-{secrets.token_hex(4)}"


class User(Base):
    """
    User model - stores authenticated users.
    No personal data stored (anonymous usernames).
    Identity is tracked via Entra ID object ID (oid).
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Anonymous identifier (not personally identifiable)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Entra ID identifiers (used for OAuth validation)
    entra_oid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)  # Object ID
    entra_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Email (for reference, not displayed)
    
    # Role (student or professor)
    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)
    
    # Tracking
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    @classmethod
    def create_or_update(cls, session, entra_oid: str, entra_email: str, role: str = "student") -> "User":
        """
        Create a new user or update existing one with latest info from Entra ID.
        Returns the user object.
        """
        # Check if user already exists
        user = session.query(cls).filter(cls.entra_oid == entra_oid).first()
        
        if user:
            # Update existing user
            user.last_login = datetime.utcnow()
            user.entra_email = entra_email  # Update email in case it changed
            user.role = role
        else:
            # Create new user with unique anonymous username
            user = cls(
                username=generate_unique_username(session),
                entra_oid=entra_oid,
                entra_email=entra_email,
                role=role,
                last_login=datetime.utcnow(),
            )
            session.add(user)
        
        session.commit()
        return user
