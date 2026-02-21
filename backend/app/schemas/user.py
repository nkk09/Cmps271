"""
Pydantic schemas for authentication and user responses.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserResponse(BaseModel):
    """User response - no PII exposed, only anonymous username."""
    id: int
    username: str  # Anonymous username only
    role: str  # "student" or "professor"
    created_at: datetime
    
    class Config:
        from_attributes = True


class CurrentUserResponse(BaseModel):
    """Current user response (for logged-in user)."""
    id: int
    username: str  # Anonymous username
    role: str
    entra_email: str  # Only show to self
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """OAuth login initiation."""
    email: str
