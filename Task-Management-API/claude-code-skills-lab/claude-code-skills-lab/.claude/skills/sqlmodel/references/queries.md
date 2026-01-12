# SQLModel Queries Reference

Comprehensive guide for querying databases with SQLModel, including filtering, pagination, joins, and optimization.

## Table of Contents
- Basic Queries
- Filtering and Conditions
- Sorting and Ordering
- Pagination
- Joins and Relationships
- Aggregations
- Advanced Patterns
- Performance Optimization

## Basic Queries

### Get All Records

```python
from sqlmodel import Session, select


def get_all_heroes(session: Session):
    statement = select(Hero)
    heroes = session.exec(statement).all()
    return heroes
```

### Get Single Record by ID

```python
def get_hero(session: Session, hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Get First Match

```python
def get_first_hero_by_name(session: Session, name: str):
    statement = select(Hero).where(Hero.name == name)
    hero = session.exec(statement).first()
    return hero
```

## Filtering and Conditions

### Simple Filters

```python
# Equality
statement = select(Hero).where(Hero.name == "Spider-Man")

# Greater than / Less than
statement = select(Hero).where(Hero.age > 18)
statement = select(Hero).where(Hero.age >= 21)

# Not equal
statement = select(Hero).where(Hero.name != "Deadpool")

# In list
statement = select(Hero).where(Hero.name.in_(["Spider-Man", "Batman", "Superman"]))

# Like (pattern matching)
statement = select(Hero).where(Hero.name.like("%man%"))

# IS NULL / IS NOT NULL
statement = select(Hero).where(Hero.age.is_(None))
statement = select(Hero).where(Hero.age.is_not(None))
```

### Multiple Conditions (AND / OR)

```python
from sqlmodel import and_, or_


# AND - all conditions must be true
statement = select(Hero).where(
    and_(
        Hero.age >= 18,
        Hero.age <= 65,
        Hero.team_id == 1
    )
)

# OR - any condition can be true
statement = select(Hero).where(
    or_(
        Hero.name == "Spider-Man",
        Hero.name == "Batman"
    )
)

# Combining AND/OR
statement = select(Hero).where(
    and_(
        Hero.age >= 18,
        or_(
            Hero.team_id == 1,
            Hero.team_id == 2
        )
    )
)

# Shorthand for AND (multiple where clauses)
statement = select(Hero).where(Hero.age >= 18).where(Hero.team_id == 1)
```

## Sorting and Ordering

```python
# Order by single column (ascending)
statement = select(Hero).order_by(Hero.name)

# Order by descending
statement = select(Hero).order_by(Hero.age.desc())

# Order by multiple columns
statement = select(Hero).order_by(Hero.team_id, Hero.name)

# Mixed ordering
statement = select(Hero).order_by(Hero.team_id.desc(), Hero.name.asc())
```

## Pagination

### Offset and Limit

```python
from fastapi import Query


@app.get("/heroes/", response_model=List[HeroRead])
def read_heroes(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    statement = select(Hero).offset(offset).limit(limit)
    heroes = session.exec(statement).all()
    return heroes
```

### With Total Count

```python
from sqlmodel import func


@app.get("/heroes/")
def read_heroes_with_count(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    # Get total count
    count_statement = select(func.count()).select_from(Hero)
    total = session.exec(count_statement).one()

    # Get paginated results
    statement = select(Hero).offset(offset).limit(limit)
    heroes = session.exec(statement).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": heroes
    }
```

### Cursor-Based Pagination

```python
@app.get("/heroes/")
def read_heroes_cursor(
    cursor_id: Optional[int] = None,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    statement = select(Hero).order_by(Hero.id)

    if cursor_id:
        statement = statement.where(Hero.id > cursor_id)

    heroes = session.exec(statement.limit(limit)).all()

    next_cursor = heroes[-1].id if heroes else None

    return {
        "items": heroes,
        "next_cursor": next_cursor
    }
```

## Joins and Relationships

### Eager Loading (Fetch Related Data)

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload


# Load heroes with their teams
statement = select(Hero).options(selectinload(Hero.team))
heroes = session.exec(statement).all()

# Now you can access hero.team without additional queries
for hero in heroes:
    print(f"{hero.name} - Team: {hero.team.name}")
```

### Filtering by Related Model

```python
# Get all heroes from a specific team
statement = select(Hero).where(Hero.team_id == 1)

# Using join for complex filtering
statement = (
    select(Hero)
    .join(Team)
    .where(Team.name == "Avengers")
)
heroes = session.exec(statement).all()
```

### Selecting Multiple Models

```python
# Select both Hero and Team
statement = select(Hero, Team).join(Team)
results = session.exec(statement).all()

for hero, team in results:
    print(f"{hero.name} is in {team.name}")
```

### Many-to-Many Queries

```python
# Get all teams for a specific hero
statement = (
    select(Team)
    .join(HeroTeamLink)
    .where(HeroTeamLink.hero_id == hero_id)
)
teams = session.exec(statement).all()
```

## Aggregations

### Count

```python
from sqlmodel import func


# Count all heroes
statement = select(func.count()).select_from(Hero)
count = session.exec(statement).one()

# Count with filter
statement = select(func.count()).select_from(Hero).where(Hero.age >= 18)
adult_count = session.exec(statement).one()

# Count by group
statement = (
    select(Hero.team_id, func.count(Hero.id))
    .group_by(Hero.team_id)
)
results = session.exec(statement).all()
```

### Sum, Average, Min, Max

```python
# Average age
statement = select(func.avg(Hero.age))
avg_age = session.exec(statement).one()

# Sum
statement = select(func.sum(Product.stock))
total_stock = session.exec(statement).one()

# Min and Max
statement = select(func.min(Hero.age), func.max(Hero.age))
min_age, max_age = session.exec(statement).one()
```

### Group By

```python
# Count heroes per team
statement = (
    select(Team.name, func.count(Hero.id))
    .join(Team)
    .group_by(Team.name)
)
results = session.exec(statement).all()

for team_name, hero_count in results:
    print(f"{team_name}: {hero_count} heroes")
```

## Advanced Patterns

### Dynamic Filtering

```python
def get_heroes_filtered(
    session: Session,
    name: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    team_id: Optional[int] = None
):
    statement = select(Hero)

    if name:
        statement = statement.where(Hero.name.like(f"%{name}%"))

    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)

    if max_age is not None:
        statement = statement.where(Hero.age <= max_age)

    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)

    return session.exec(statement).all()
```

### Subqueries

```python
# Get heroes older than the average age
avg_age_statement = select(func.avg(Hero.age))
avg_age = session.exec(avg_age_statement).one()

statement = select(Hero).where(Hero.age > avg_age)
heroes = session.exec(statement).all()

# Using subquery in the statement
subquery = select(func.avg(Hero.age)).scalar_subquery()
statement = select(Hero).where(Hero.age > subquery)
heroes = session.exec(statement).all()
```

### Exists Queries

```python
from sqlmodel import exists


# Check if any hero with name exists
statement = select(exists().where(Hero.name == "Spider-Man"))
hero_exists = session.exec(statement).one()
```

### Raw SQL (When Necessary)

```python
from sqlmodel import text


# Use raw SQL for complex queries
statement = text("""
    SELECT h.*, t.name as team_name
    FROM hero h
    LEFT JOIN team t ON h.team_id = t.id
    WHERE h.age > :min_age
""")

results = session.exec(statement, {"min_age": 18})
```

## Performance Optimization

### 1. Use Pagination Always

```python
# Bad - loads everything into memory
all_heroes = session.exec(select(Hero)).all()

# Good - paginate
heroes = session.exec(select(Hero).limit(100)).all()
```

### 2. Eager Load Relationships to Avoid N+1 Queries

```python
from sqlalchemy.orm import selectinload

# Bad - N+1 query problem
heroes = session.exec(select(Hero)).all()
for hero in heroes:
    print(hero.team.name)  # Separate query for each hero!

# Good - eager loading
heroes = session.exec(
    select(Hero).options(selectinload(Hero.team))
).all()
for hero in heroes:
    print(hero.team.name)  # No additional queries
```

### 3. Select Only Required Columns

```python
# Bad - selects all columns
heroes = session.exec(select(Hero)).all()

# Good - select only what you need
statement = select(Hero.id, Hero.name)
results = session.exec(statement).all()
```

### 4. Use Indexes

```python
# Add indexes for frequently queried columns
class Hero(SQLModel, table=True):
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    team_id: int = Field(foreign_key="team.id", index=True)
```

### 5. Batch Operations

```python
# Bad - multiple individual inserts
for hero_data in hero_list:
    hero = Hero(**hero_data)
    session.add(hero)
    session.commit()  # Don't commit inside loop!

# Good - batch insert
for hero_data in hero_list:
    hero = Hero(**hero_data)
    session.add(hero)
session.commit()  # Single commit
```

### 6. Use Exists Instead of Count for Checking

```python
# Bad - counts all records
count = session.exec(select(func.count()).select_from(Hero).where(Hero.name == "Spider-Man")).one()
if count > 0:
    ...

# Good - stops at first match
exists_statement = select(exists().where(Hero.name == "Spider-Man"))
if session.exec(exists_statement).one():
    ...
```
