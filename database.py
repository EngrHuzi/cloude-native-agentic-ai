"""
Database configuration and session management
"""
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable and remove quotes if present
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_db"
).strip("'\"")

# For async operations, use asyncpg driver
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
)

# Async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session():
    """Dependency for getting async database sessions"""
    async with async_session_maker() as session:
        yield session
