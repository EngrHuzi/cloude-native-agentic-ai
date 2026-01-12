---
name: sqlmodel
description: SQLModel development for FastAPI applications using uv package manager. Use when working with SQLModel or when the user requests to create database models, CRUD operations, database queries, migrations with Alembic, or any SQL database tasks in FastAPI. Includes 'uv add' for dependencies, 'uv run' for commands, code generation scripts, comprehensive reference documentation, and a basic project template for SQLModel + FastAPI development.
---

# SQLModel for FastAPI

SQLModel combines SQLAlchemy and Pydantic to provide a unified way to define database models and API schemas in FastAPI applications.

## Quick Start

### Using the Basic Template

Copy the basic template to start a new project:

```bash
# Initialize new project
uv init my-sqlmodel-app
cd my-sqlmodel-app

# Copy template files
cp -r assets/basic-template/* ./

# Add dependencies
uv add "fastapi[standard]" sqlmodel

# Run the application
uv run fastapi dev main.py
```

The template includes:
- Database configuration with SQLite (easily switchable to PostgreSQL)
- Hero model with CRUD endpoints
- Proper separation of database models and API schemas
- Pagination support

### Generate Individual Components

Use scripts to generate specific components:

```bash
# Generate a model
uv run python scripts/generate_model.py User --fields "name:str" "email:str" "age:Optional[int]=None"

# Generate CRUD endpoints
uv run python scripts/generate_crud.py User --output routes/users.py

# Initialize Alembic for migrations
uv run python scripts/init_alembic.py --database-url "sqlite:///./database.db"
```

## Core Tasks

### 1. Creating Models

For detailed model creation patterns, see [references/models.md](references/models.md).

#### Basic Model

```python
from typing import Optional
from sqlmodel import SQLModel, Field


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = None
```

#### With Relationships

```python
class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    heroes: List["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    team_id: Optional[int] = Field(foreign_key="team.id")

    team: Optional[Team] = Relationship(back_populates="heroes")
```

#### Schema Models for APIs

Always separate database models from API schemas:

```python
# Database model
class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str


# API schemas
class HeroCreate(SQLModel):  # For POST
    name: str
    secret_name: str


class HeroRead(SQLModel):  # For GET
    id: int
    name: str
    secret_name: str


class HeroUpdate(SQLModel):  # For PATCH/PUT
    name: Optional[str] = None
    secret_name: Optional[str] = None
```

**Code generation:** Use `uv run python scripts/generate_model.py` to generate model boilerplate.

**Reference:** See `references/models.md` for:
- Field types and validation
- One-to-many and many-to-many relationships
- Indexes and constraints
- Best practices

### 2. Building CRUD Endpoints

#### Basic CRUD Pattern

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select


@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=List[HeroRead])
def read_heroes(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(
    hero_id: int,
    hero_update: HeroUpdate,
    session: Session = Depends(get_session)
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero_update.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

**Code generation:** Use `uv run python scripts/generate_crud.py` to generate complete CRUD endpoints.

### 3. Querying Data

For comprehensive query patterns, see [references/queries.md](references/queries.md).

#### Common Query Patterns

```python
from sqlmodel import select, and_, or_, func


# Simple filter
heroes = session.exec(select(Hero).where(Hero.age > 18)).all()

# Multiple conditions
heroes = session.exec(
    select(Hero).where(and_(Hero.age >= 18, Hero.team_id == 1))
).all()

# Pagination with count
count = session.exec(select(func.count()).select_from(Hero)).one()
heroes = session.exec(select(Hero).offset(0).limit(100)).all()

# Eager loading relationships
from sqlalchemy.orm import selectinload

heroes = session.exec(
    select(Hero).options(selectinload(Hero.team))
).all()
```

**Reference:** See `references/queries.md` for:
- Filtering and conditions (AND/OR, LIKE, IN, NULL checks)
- Sorting and pagination
- Joins and relationship queries
- Aggregations (COUNT, SUM, AVG)
- Performance optimization

### 4. Database Migrations

For detailed migration workflows, see [references/migrations.md](references/migrations.md).

#### Setup Alembic

```bash
# Add Alembic dependency
uv add alembic

# Initialize Alembic (creates alembic/ directory and config)
uv run python scripts/init_alembic.py --database-url "sqlite:///./database.db"

# Import all models in alembic/env.py
# from app.models import Hero, Team, User
```

#### Create and Apply Migrations

```bash
# Create migration from model changes
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

#### Manual Migration Operations

```python
# In migration file
def upgrade():
    op.create_table(
        'hero',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
    )

    op.add_column('hero', sa.Column('email', sa.String(255)))

    op.create_index('ix_hero_name', 'hero', ['name'])
```

**Script:** Use `uv run python scripts/init_alembic.py` to set up Alembic with SQLModel configuration.

**Reference:** See `references/migrations.md` for:
- Creating and applying migrations
- Common migration operations
- Data migrations
- Best practices and troubleshooting

### 5. Testing

For comprehensive testing strategies, see [references/testing.md](references/testing.md).

#### Test Setup

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
```

#### Test CRUD Operations

```python
def test_create_hero(client):
    response = client.post(
        "/heroes/",
        json={"name": "Spider-Man", "secret_name": "Peter Parker", "age": 25}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Spider-Man"


def test_read_hero(client, hero_fixture):
    response = client.get(f"/heroes/{hero_fixture.id}")
    assert response.status_code == 200
    assert response.json()["id"] == hero_fixture.id
```

**Run tests:**
```bash
# Add test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
uv run pytest
uv run pytest --cov=app --cov-report=html
```

**Reference:** See `references/testing.md` for:
- Test database setup and fixtures
- Testing CRUD operations
- Testing relationships
- Testing validation
- Integration tests

## Database Configuration

### SQLite (Development)

```python
from sqlmodel import create_engine

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)
```

### PostgreSQL (Production)

```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable in production
)
```

### Session Management

```python
from sqlmodel import Session


def get_session():
    with Session(engine) as session:
        yield session


# Use in FastAPI endpoints
@app.get("/heroes/")
def read_heroes(session: Session = Depends(get_session)):
    ...
```

## Best Practices

1. **Use uv for package management**: Install with `uv add`, run with `uv run`
2. **Separate models from schemas**: Use `table=True` for database models, create separate classes for API request/response
3. **Always use pagination**: Limit query results with `.offset()` and `.limit()`
4. **Eager load relationships**: Use `selectinload()` to avoid N+1 query problems
5. **Validate at the model level**: Use Field constraints (`ge`, `le`, `min_length`, etc.)
6. **Use `model_validate()` for creation**: When creating from schemas
7. **Use `model_dump(exclude_unset=True)` for updates**: Only update provided fields
8. **Index foreign keys**: Always add `index=True` to foreign key fields
9. **Test with in-memory database**: Use SQLite in-memory for fast tests

## Resources

- **scripts/**: Code generation utilities
  - `generate_model.py` - Generate SQLModel classes
  - `generate_crud.py` - Generate CRUD endpoints
  - `init_alembic.py` - Initialize Alembic migrations

- **references/**: Comprehensive guides
  - `models.md` - Model creation, relationships, validation
  - `queries.md` - Query patterns, filtering, pagination
  - `migrations.md` - Database migrations with Alembic
  - `testing.md` - Testing strategies and best practices

- **assets/basic-template/**: Full working FastAPI + SQLModel project template
