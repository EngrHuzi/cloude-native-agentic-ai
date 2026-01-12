"""
Authentication-related schemas
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    """User login credentials"""
    username: str
    password: str
