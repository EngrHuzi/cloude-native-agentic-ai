# Testing SQLModel Applications

Guide for testing FastAPI applications using SQLModel with pytest.

## Table of Contents
- Test Setup and Configuration
- Database Fixtures
- Testing CRUD Operations
- Testing with Relationships
- Testing Validation
- Integration Tests
- Test Best Practices

## Test Setup and Configuration

### Install Testing Dependencies

```bash
# Add testing dependencies with uv
uv add --dev pytest pytest-cov httpx pytest-asyncio
```

### Test Database Configuration

Create `tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
```

## Database Fixtures

### Basic Model Fixture

```python
@pytest.fixture
def hero_fixture(session: Session):
    """Create a test hero"""
    hero = Hero(name="Spider-Man", secret_name="Peter Parker", age=25)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@pytest.fixture
def multiple_heroes_fixture(session: Session):
    """Create multiple test heroes"""
    heroes = [
        Hero(name="Spider-Man", secret_name="Peter Parker", age=25),
        Hero(name="Batman", secret_name="Bruce Wayne", age=35),
        Hero(name="Superman", secret_name="Clark Kent", age=30),
    ]
    for hero in heroes:
        session.add(hero)
    session.commit()
    return heroes
```

### Fixtures with Relationships

```python
@pytest.fixture
def team_with_heroes_fixture(session: Session):
    """Create a team with heroes"""
    team = Team(name="Avengers", headquarters="New York")
    session.add(team)
    session.commit()
    session.refresh(team)

    heroes = [
        Hero(name="Iron Man", secret_name="Tony Stark", age=40, team_id=team.id),
        Hero(name="Thor", secret_name="Thor Odinson", age=1500, team_id=team.id),
    ]
    for hero in heroes:
        session.add(hero)

    session.commit()
    return team, heroes
```

## Testing CRUD Operations

### Test Create

```python
def test_create_hero(client):
    """Test creating a hero via API"""
    response = client.post(
        "/heroes/",
        json={
            "name": "Spider-Man",
            "secret_name": "Peter Parker",
            "age": 25
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Spider-Man"
    assert data["secret_name"] == "Peter Parker"
    assert data["age"] == 25
    assert "id" in data


def test_create_hero_direct(session):
    """Test creating a hero directly in database"""
    hero = Hero(name="Batman", secret_name="Bruce Wayne", age=35)
    session.add(hero)
    session.commit()
    session.refresh(hero)

    assert hero.id is not None
    assert hero.name == "Batman"
```

### Test Read

```python
def test_read_hero(client, hero_fixture):
    """Test reading a hero"""
    response = client.get(f"/heroes/{hero_fixture.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == hero_fixture.id
    assert data["name"] == hero_fixture.name


def test_read_heroes_list(client, multiple_heroes_fixture):
    """Test reading list of heroes"""
    response = client.get("/heroes/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Spider-Man"


def test_read_nonexistent_hero(client):
    """Test reading a hero that doesn't exist"""
    response = client.get("/heroes/9999")
    assert response.status_code == 404
```

### Test Update

```python
def test_update_hero(client, hero_fixture):
    """Test updating a hero"""
    response = client.patch(
        f"/heroes/{hero_fixture.id}",
        json={"age": 26}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["age"] == 26
    assert data["name"] == hero_fixture.name  # Unchanged


def test_update_nonexistent_hero(client):
    """Test updating a hero that doesn't exist"""
    response = client.patch(
        "/heroes/9999",
        json={"age": 30}
    )
    assert response.status_code == 404
```

### Test Delete

```python
def test_delete_hero(client, hero_fixture):
    """Test deleting a hero"""
    response = client.delete(f"/heroes/{hero_fixture.id}")
    assert response.status_code == 200

    # Verify hero is deleted
    response = client.get(f"/heroes/{hero_fixture.id}")
    assert response.status_code == 404


def test_delete_nonexistent_hero(client):
    """Test deleting a hero that doesn't exist"""
    response = client.delete("/heroes/9999")
    assert response.status_code == 404
```

## Testing with Relationships

### Test Creating with Relationships

```python
def test_create_hero_with_team(client, session):
    """Test creating a hero and associating with a team"""
    # Create team first
    team = Team(name="Avengers", headquarters="New York")
    session.add(team)
    session.commit()
    session.refresh(team)

    # Create hero with team
    response = client.post(
        "/heroes/",
        json={
            "name": "Iron Man",
            "secret_name": "Tony Stark",
            "age": 40,
            "team_id": team.id
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["team_id"] == team.id
```

### Test Eager Loading

```python
def test_hero_with_team_relationship(session, team_with_heroes_fixture):
    """Test querying heroes with team relationship"""
    from sqlmodel import select
    from sqlalchemy.orm import selectinload

    team, heroes = team_with_heroes_fixture

    # Query with eager loading
    statement = select(Hero).options(selectinload(Hero.team))
    db_hero = session.exec(statement).first()

    assert db_hero is not None
    assert db_hero.team is not None
    assert db_hero.team.name == "Avengers"
```

### Test Many-to-Many Relationships

```python
def test_many_to_many_relationship(session):
    """Test many-to-many relationship between heroes and teams"""
    # Create heroes
    hero1 = Hero(name="Spider-Man", secret_name="Peter Parker")
    hero2 = Hero(name="Iron Man", secret_name="Tony Stark")

    # Create teams
    team1 = Team(name="Avengers", headquarters="New York")
    team2 = Team(name="Defenders", headquarters="New York")

    # Link heroes to teams
    hero1.teams = [team1, team2]
    hero2.teams = [team1]

    session.add(hero1)
    session.add(hero2)
    session.commit()

    # Verify relationships
    assert len(hero1.teams) == 2
    assert len(hero2.teams) == 1
    assert len(team1.heroes) == 2
    assert len(team2.heroes) == 1
```

## Testing Validation

### Test Field Validation

```python
def test_hero_age_validation(client):
    """Test that age validation works"""
    # Age too high
    response = client.post(
        "/heroes/",
        json={
            "name": "Ancient One",
            "secret_name": "???",
            "age": 500  # Assuming max is 200
        }
    )
    assert response.status_code == 422  # Validation error


def test_hero_name_required(client):
    """Test that name is required"""
    response = client.post(
        "/heroes/",
        json={
            "secret_name": "Peter Parker",
            "age": 25
        }
    )
    assert response.status_code == 422


def test_hero_email_format(client):
    """Test email format validation"""
    response = client.post(
        "/users/",
        json={
            "name": "John Doe",
            "email": "invalid-email"  # Invalid format
        }
    )
    assert response.status_code == 422
```

### Test Unique Constraints

```python
def test_unique_email_constraint(client, session):
    """Test that email must be unique"""
    # Create first user
    response1 = client.post(
        "/users/",
        json={"name": "John", "email": "john@example.com"}
    )
    assert response1.status_code == 200

    # Try to create second user with same email
    response2 = client.post(
        "/users/",
        json={"name": "Jane", "email": "john@example.com"}
    )
    # Should fail with 400 or 409
    assert response2.status_code in [400, 409]
```

## Integration Tests

### Test Complete Workflow

```python
def test_complete_hero_workflow(client):
    """Test creating, reading, updating, and deleting a hero"""
    # Create
    create_response = client.post(
        "/heroes/",
        json={
            "name": "Spider-Man",
            "secret_name": "Peter Parker",
            "age": 25
        }
    )
    assert create_response.status_code == 200
    hero_id = create_response.json()["id"]

    # Read
    read_response = client.get(f"/heroes/{hero_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Spider-Man"

    # Update
    update_response = client.patch(
        f"/heroes/{hero_id}",
        json={"age": 26}
    )
    assert update_response.status_code == 200
    assert update_response.json()["age"] == 26

    # Delete
    delete_response = client.delete(f"/heroes/{hero_id}")
    assert delete_response.status_code == 200

    # Verify deletion
    read_deleted = client.get(f"/heroes/{hero_id}")
    assert read_deleted.status_code == 404
```

### Test Pagination

```python
def test_pagination(client, session):
    """Test pagination of heroes list"""
    # Create 150 heroes
    for i in range(150):
        hero = Hero(name=f"Hero {i}", secret_name=f"Secret {i}")
        session.add(hero)
    session.commit()

    # Get first page
    response1 = client.get("/heroes/?offset=0&limit=50")
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) == 50

    # Get second page
    response2 = client.get("/heroes/?offset=50&limit=50")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 50

    # Ensure different results
    assert data1[0]["id"] != data2[0]["id"]
```

## Test Best Practices

### 1. Use Isolated Test Database

Always use an in-memory or separate test database:

```python
engine = create_engine(
    "sqlite:///:memory:",  # In-memory for speed
    poolclass=StaticPool,
)
```

### 2. Clean Database Between Tests

Use fixtures to ensure clean state:

```python
@pytest.fixture(autouse=True)
def reset_db(session):
    """Reset database after each test"""
    yield
    session.rollback()
```

### 3. Test Edge Cases

```python
def test_empty_list(client):
    """Test getting heroes when none exist"""
    response = client.get("/heroes/")
    assert response.status_code == 200
    assert response.json() == []


def test_large_offset(client):
    """Test pagination with offset larger than total"""
    response = client.get("/heroes/?offset=1000")
    assert response.status_code == 200
    assert response.json() == []
```

### 4. Use Parametrize for Multiple Cases

```python
@pytest.mark.parametrize("age,expected_status", [
    (0, 200),      # Minimum valid
    (200, 200),    # Maximum valid
    (-1, 422),     # Below minimum
    (201, 422),    # Above maximum
])
def test_hero_age_boundaries(client, age, expected_status):
    """Test age validation boundaries"""
    response = client.post(
        "/heroes/",
        json={"name": "Test", "secret_name": "Test", "age": age}
    )
    assert response.status_code == expected_status
```

### 5. Test Error Messages

```python
def test_validation_error_message(client):
    """Test that validation errors provide helpful messages"""
    response = client.post(
        "/heroes/",
        json={"secret_name": "Peter Parker"}  # Missing name
    )

    assert response.status_code == 422
    error = response.json()
    assert "name" in str(error).lower()
```

### 6. Use Test Coverage

```bash
# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 7. Organize Tests by Feature

```
tests/
├── conftest.py
├── test_heroes.py
├── test_teams.py
├── test_auth.py
└── test_integration.py
```
