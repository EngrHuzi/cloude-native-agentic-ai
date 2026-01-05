"""
Pytest configuration and fixtures for Todo Management API tests
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_async_session


# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Test session maker
test_async_session_maker = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(name="session")
async def session_fixture():
    """Create a fresh database for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession):
    """Create test client with test database"""
    async def get_session_override():
        yield session

    app.dependency_overrides[get_async_session] = get_session_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_todo_data():
    """Sample todo data for testing"""
    return {
        "title": "Test Todo",
        "description": "This is a test todo",
        "status": "todo",
        "priority": "medium"
    }
