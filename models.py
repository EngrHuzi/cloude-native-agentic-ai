"""
SQLModel models for Todo Management API
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class TodoStatus(str, Enum):
    """Todo status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    """Todo priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Database Model (table=True)
class Todo(SQLModel, table=True):
    """Todo database model"""
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TodoStatus = Field(default=TodoStatus.TODO)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to User
    user_id: int = Field(foreign_key="users.id", index=True)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="todos")


# Schema Models for API

class TodoBase(SQLModel):
    """Base schema with shared fields"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TodoStatus = Field(default=TodoStatus.TODO)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    """Schema for creating todos"""
    pass


class TodoRead(TodoBase):
    """Schema for reading todos"""
    id: int
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TodoUpdate(SQLModel):
    """Schema for updating todos (all fields optional)"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None


class TodoSummary(SQLModel):
    """Summary statistics for todos"""
    total: int
    todo: int
    in_progress: int
    completed: int
    high_priority: int
    overdue: int


# User Models

class User(SQLModel, table=True):
    """User database model"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field(min_length=1)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    todos: list["Todo"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """Schema for creating users"""
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserRead(SQLModel):
    """Schema for reading user data (public info only)"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
