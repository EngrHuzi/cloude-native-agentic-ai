# Testing Guide

Complete guide for testing FastAPI applications with pytest, async tests, and test coverage.

## Table of Contents

- Setup and Configuration
- Basic Testing with TestClient
- Async Testing
- Database Testing
- Authentication Testing
- Test Fixtures
- Mocking and Patching
- Test Coverage
- Integration Testing

## Setup and Configuration

### Dependencies

```bash
uv add --dev pytest pytest-asyncio httpx pytest-cov
```

### pytest Configuration (`pytest.ini` or `pyproject.toml`)

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "--cov=app --cov-report=html --cov-report=term-missing"
```

## Basic Testing with TestClient

### Simple Tests (`tests/test_main.py`)

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_item():
    """Test item creation."""
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 10.99
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert "id" in data


def test_get_item():
    """Test getting an item."""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_item_not_found():
    """Test 404 for non-existent item."""
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_validation_error():
    """Test validation error."""
    invalid_data = {
        "name": "Test",
        "price": "invalid"  # Should be a number
    }
    response = client.post("/items/", json=invalid_data)
    assert response.status_code == 422
```

## Async Testing

### Async Test Client (`tests/test_async.py`)

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_async_create_item():
    """Test async item creation."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        item_data = {
            "name": "Async Item",
            "price": 29.99
        }
        response = await client.post("/items/", json=item_data)
        assert response.status_code == 201
        assert response.json()["name"] == "Async Item"


@pytest.mark.asyncio
async def test_async_list_items():
    """Test async listing items."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/items/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

## Database Testing

### Test Database Setup (`tests/conftest.py`)

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from database import Base, get_db
from main import app

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    """Create test client with test database."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

### Database Tests (`tests/test_database.py`)

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import crud
import schemas


@pytest.mark.asyncio
async def test_create_user(test_db: AsyncSession):
    """Test creating a user in database."""
    user_data = schemas.UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )

    user = await crud.create_user(test_db, user_data)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user(test_db: AsyncSession):
    """Test retrieving a user."""
    # Create user first
    user_data = schemas.UserCreate(
        username="getuser",
        email="get@example.com",
        password="password"
    )
    created_user = await crud.create_user(test_db, user_data)

    # Retrieve user
    fetched_user = await crud.get_user(test_db, created_user.id)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.username == "getuser"


@pytest.mark.asyncio
async def test_create_duplicate_user(test_db: AsyncSession, client):
    """Test creating duplicate user fails."""
    user_data = {
        "username": "duplicate",
        "email": "dup@example.com",
        "password": "password"
    }

    # Create first user
    response1 = await client.post("/users/", json=user_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = await client.post("/users/", json=user_data)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"].lower()
```

## Authentication Testing

### Auth Test Fixtures (`tests/test_auth.py`)

```python
import pytest
from httpx import AsyncClient


@pytest_asyncio.fixture
async def test_user(client: AsyncClient):
    """Create a test user and return credentials."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return {
        "username": user_data["username"],
        "password": user_data["password"],
        "tokens": response.json()
    }


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, test_user):
    """Return client with auth headers."""
    client.headers["Authorization"] = f"Bearer {test_user['tokens']['access_token']}"
    return client


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    }
    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    """Test user login."""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = await client.post("/auth/login", data=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_protected_route(authenticated_client: AsyncClient):
    """Test accessing protected route."""
    response = await authenticated_client.get("/auth/me")

    assert response.status_code == 200
    assert "username" in response.json()


@pytest.mark.asyncio
async def test_protected_route_unauthorized(client: AsyncClient):
    """Test protected route without authentication."""
    response = await client.get("/auth/me")
    assert response.status_code == 401
```

## Test Fixtures

### Common Fixtures (`tests/conftest.py`)

```python
import pytest
import pytest_asyncio
from typing import List
import models


@pytest_asyncio.fixture
async def sample_items(test_db) -> List[models.Item]:
    """Create sample items for testing."""
    items = []
    for i in range(5):
        item = models.Item(
            title=f"Item {i}",
            description=f"Description {i}",
            price=10.0 * (i + 1),
            owner_id=1
        )
        test_db.add(item)
        items.append(item)

    await test_db.flush()
    return items


@pytest.fixture
def sample_item_data():
    """Return sample item data."""
    return {
        "title": "Test Item",
        "description": "A test item",
        "price": 19.99
    }
```

## Mocking and Patching

### Mocking External APIs (`tests/test_mocks.py`)

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
@patch("services.external_api.fetch_data")
async def test_external_api_call(mock_fetch, client):
    """Test mocking external API."""
    # Mock the external API response
    mock_fetch.return_value = {"data": "mocked"}

    response = await client.get("/api/external-data")

    assert response.status_code == 200
    assert response.json() == {"data": "mocked"}
    mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_email_sending(client, monkeypatch):
    """Test mocking email sending."""
    mock_send = AsyncMock(return_value=True)
    monkeypatch.setattr("services.email.send_email", mock_send)

    response = await client.post("/users/", json={
        "username": "newuser",
        "email": "user@example.com",
        "password": "password"
    })

    assert response.status_code == 201
    mock_send.assert_called_once()
```

## Test Coverage

### Running Tests with Coverage

```bash
# Run tests with coverage
pytest

# Run specific test file
pytest tests/test_main.py

# Run tests matching pattern
pytest -k "test_create"

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Coverage Configuration (`.coveragerc`)

```ini
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Integration Testing

### End-to-End Tests (`tests/test_integration.py`)

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_user_flow(client: AsyncClient):
    """Test complete user registration, login, and data access flow."""

    # 1. Register user
    user_data = {
        "username": "integrationuser",
        "email": "integration@example.com",
        "password": "password123"
    }
    register_response = await client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    tokens = register_response.json()

    # 2. Access protected endpoint
    client.headers["Authorization"] = f"Bearer {tokens['access_token']}"
    me_response = await client.get("/auth/me")
    assert me_response.status_code == 200
    user = me_response.json()

    # 3. Create item
    item_data = {
        "title": "Integration Test Item",
        "description": "Created during integration test",
        "price": 99.99
    }
    create_response = await client.post("/items/", json=item_data)
    assert create_response.status_code == 201
    item = create_response.json()

    # 4. Get item
    get_response = await client.get(f"/items/{item['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == item_data["title"]

    # 5. Update item
    update_data = {"price": 79.99}
    update_response = await client.put(f"/items/{item['id']}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 79.99

    # 6. Delete item
    delete_response = await client.delete(f"/items/{item['id']}")
    assert delete_response.status_code == 204

    # 7. Verify deletion
    verify_response = await client.get(f"/items/{item['id']}")
    assert verify_response.status_code == 404
```

## Best Practices

1. **Use fixtures** for common setup and teardown
2. **Test edge cases** and error conditions
3. **Mock external dependencies** to isolate tests
4. **Use meaningful test names** that describe what is being tested
5. **Keep tests independent** - each test should run in isolation
6. **Test both success and failure paths**
7. **Use parametrized tests** for testing multiple scenarios
8. **Aim for high coverage** but focus on meaningful tests
9. **Test security** - authentication, authorization, input validation
10. **Use async fixtures** for async database operations

## Parametrized Tests

```python
import pytest


@pytest.mark.parametrize("price,expected_status", [
    (10.0, 201),
    (0.0, 201),
    (-1.0, 422),  # Negative price should fail validation
])
@pytest.mark.asyncio
async def test_item_price_validation(client, price, expected_status):
    """Test item price validation with various values."""
    item_data = {
        "title": "Test Item",
        "price": price
    }
    response = await client.post("/items/", json=item_data)
    assert response.status_code == expected_status
```
