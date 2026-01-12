# SQLModel Models Reference

Comprehensive guide for creating SQLModel classes with relationships, validation, and best practices.

## Table of Contents
- Basic Model Creation
- Field Types and Validation
- Relationships (One-to-Many, Many-to-Many)
- Schema Models (Create, Read, Update)
- Indexes and Constraints
- Best Practices

## Basic Model Creation

```python
from typing import Optional
from sqlmodel import SQLModel, Field


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, ge=0, le=200)
```

Key points:
- `table=True` creates a database table
- `id` field with `primary_key=True` is standard
- Use `Optional` for nullable fields
- Set `default=None` for optional fields

## Field Types and Validation

### Common Field Types

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # String fields
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

    # Numeric fields
    price: Decimal = Field(decimal_places=2, gt=0)
    stock: int = Field(ge=0)  # Greater than or equal to 0

    # Boolean
    is_active: bool = Field(default=True)

    # Datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

### Field Validation

```python
from sqlmodel import Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # String length constraints
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")

    # Numeric constraints
    age: int = Field(ge=18, le=120)  # Between 18 and 120
    score: float = Field(gt=0.0, lt=100.0)  # Between 0 and 100 (exclusive)
```

## Relationships

### One-to-Many Relationship

```python
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    # One team has many heroes
    heroes: List["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

    # Foreign key
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Many heroes belong to one team
    team: Optional[Team] = Relationship(back_populates="heroes")
```

### Many-to-Many Relationship

```python
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


# Link table
class HeroTeamLink(SQLModel, table=True):
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    hero_id: Optional[int] = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: List["Hero"] = Relationship(
        back_populates="teams", link_model=HeroTeamLink
    )


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

    teams: List[Team] = Relationship(
        back_populates="heroes", link_model=HeroTeamLink
    )
```

## Schema Models (Create, Read, Update)

SQLModel best practice: Create separate models for different API operations.

```python
from typing import Optional
from sqlmodel import SQLModel, Field


# Base model with shared fields
class HeroBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    secret_name: str
    age: Optional[int] = Field(default=None, ge=0, le=200)


# Database model (table=True)
class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")


# Schema for creating heroes (no ID)
class HeroCreate(HeroBase):
    team_id: Optional[int] = None


# Schema for reading heroes (includes ID and computed fields)
class HeroRead(HeroBase):
    id: int


# Schema for updating (all fields optional)
class HeroUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    secret_name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=200)
    team_id: Optional[int] = None
```

Usage in FastAPI:

```python
@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session)
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

## Indexes and Constraints

### Single Column Index

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # Unique + indexed
    username: str = Field(index=True)  # Just indexed
```

### Composite Indexes

```python
from sqlmodel import SQLModel, Field, Index


class Log(SQLModel, table=True):
    __table_args__ = (
        Index("ix_log_user_timestamp", "user_id", "timestamp"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    action: str
    timestamp: datetime
```

### Check Constraints

```python
from sqlalchemy import CheckConstraint


class Product(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint('price > 0', name='price_positive'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: Decimal
```

## Best Practices

1. **Always use Optional for nullable fields**:
   ```python
   age: Optional[int] = Field(default=None)  # Good
   age: int = None  # Avoid - type checker warning
   ```

2. **Use Field for database-specific configuration**:
   ```python
   email: str = Field(unique=True, index=True, max_length=255)
   ```

3. **Separate table models from API schemas**:
   - `Hero` (table=True) - Database model
   - `HeroCreate` - For POST requests
   - `HeroRead` - For GET responses
   - `HeroUpdate` - For PATCH/PUT requests

4. **Use `model_validate()` when creating from schemas**:
   ```python
   db_hero = Hero.model_validate(hero_create)
   ```

5. **Use `model_dump(exclude_unset=True)` for updates**:
   ```python
   hero_data = hero_update.model_dump(exclude_unset=True)
   ```

6. **Always index foreign keys**:
   ```python
   team_id: Optional[int] = Field(default=None, foreign_key="team.id", index=True)
   ```

7. **Use meaningful back_populates names**:
   ```python
   heroes: List["Hero"] = Relationship(back_populates="team")  # Clear relationship
   ```

8. **Validate data at the model level**:
   ```python
   age: int = Field(ge=0, le=200)  # Validation in the model
   ```
