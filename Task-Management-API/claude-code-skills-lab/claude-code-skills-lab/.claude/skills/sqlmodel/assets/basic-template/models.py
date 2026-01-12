"""
Database models and schemas
"""
from typing import Optional
from sqlmodel import SQLModel, Field


# Database Model (table=True)
class Hero(SQLModel, table=True):
    """Hero database model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=100)
    secret_name: str = Field(min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, ge=0, le=200)


# Schema Models for API

class HeroBase(SQLModel):
    """Base schema with shared fields"""
    name: str = Field(min_length=1, max_length=100)
    secret_name: str = Field(min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, ge=0, le=200)


class HeroCreate(HeroBase):
    """Schema for creating heroes"""
    pass


class HeroRead(HeroBase):
    """Schema for reading heroes"""
    id: int


class HeroUpdate(SQLModel):
    """Schema for updating heroes (all fields optional)"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    secret_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    age: Optional[int] = Field(default=None, ge=0, le=200)
