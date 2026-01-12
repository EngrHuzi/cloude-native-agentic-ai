# Database Integration

Complete guide for integrating databases with FastAPI using modern async patterns.

## Table of Contents

- SQLAlchemy (Async) - PostgreSQL/SQLite
- MongoDB with Motor
- Redis for Caching
- Database Migration with Alembic

## SQLAlchemy (Async)

### Setup

```bash
uv add sqlalchemy asyncpg alembic psycopg2-binary
```

### Database Configuration (`database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

# Use PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# Or SQLite for development
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### Model Definition (`models.py`)

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="items")
```

### Pydantic Schemas (`schemas.py`)

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    items: List[Item] = []

    class Config:
        from_attributes = True
```

### CRUD Operations (`crud.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import models
import schemas


async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Get user by email."""
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users."""
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """Create new user."""
    # Hash password here (see authentication.md)
    hashed_password = "hashed_" + user.password  # Replace with proper hashing
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def create_item(db: AsyncSession, item: schemas.ItemCreate, user_id: int) -> models.Item:
    """Create new item for user."""
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    await db.flush()
    await db.refresh(db_item)
    return db_item


async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """Get list of items."""
    result = await db.execute(select(models.Item).offset(skip).limit(limit))
    return result.scalars().all()
```

### Router with Database (`routers/users.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await crud.create_user(db, user)


@router.get("/", response_model=List[schemas.User])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all users."""
    return await crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID."""
    db_user = await crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user
```

### Main App Setup

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)
```

## MongoDB with Motor

### Setup

```bash
uv add motor pymongo
```

### Configuration (`database_mongo.py`)

```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "fastapi_db"

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None

db = MongoDB()


async def get_database():
    """Get database instance."""
    return db.client[DATABASE_NAME]


async def connect_to_mongo():
    """Connect to MongoDB."""
    db.client = AsyncIOMotorClient(MONGODB_URL)


async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        db.client.close()
```

### CRUD with MongoDB

```python
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId
from database_mongo import get_database

router = APIRouter(prefix="/items", tags=["items"])


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ItemModel(BaseModel):
    id: Optional[PyObjectId] = None
    name: str
    description: str
    price: float
    created_at: datetime = datetime.utcnow()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


@router.post("/", response_model=ItemModel)
async def create_item(item: ItemModel, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Create item in MongoDB."""
    item_dict = item.model_dump(by_alias=True, exclude={"id"})
    result = await db["items"].insert_one(item_dict)
    item.id = result.inserted_id
    return item


@router.get("/", response_model=List[ItemModel])
async def list_items(db: AsyncIOMotorDatabase = Depends(get_database)):
    """List all items."""
    items = []
    async for item in db["items"].find():
        items.append(ItemModel(**item, id=item["_id"]))
    return items


@router.get("/{item_id}", response_model=ItemModel)
async def get_item(item_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get item by ID."""
    item = await db["items"].find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemModel(**item, id=item["_id"])
```

## Redis Caching

### Setup

```bash
uv add redis
```

### Configuration (`cache.py`)

```python
from redis import asyncio as aioredis
from typing import Optional
import json

class RedisCache:
    client: Optional[aioredis.Redis] = None

cache = RedisCache()


async def get_redis():
    """Get Redis client."""
    return cache.client


async def connect_to_redis():
    """Connect to Redis."""
    cache.client = await aioredis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )


async def close_redis_connection():
    """Close Redis connection."""
    if cache.client:
        await cache.client.close()


async def get_cached(key: str) -> Optional[dict]:
    """Get cached value."""
    if not cache.client:
        return None
    value = await cache.client.get(key)
    return json.loads(value) if value else None


async def set_cached(key: str, value: dict, expire: int = 3600):
    """Set cached value with expiration."""
    if cache.client:
        await cache.client.set(key, json.dumps(value), ex=expire)


async def delete_cached(key: str):
    """Delete cached value."""
    if cache.client:
        await cache.client.delete(key)
```

### Using Cache in Routes

```python
from fastapi import APIRouter, Depends
from cache import get_cached, set_cached

router = APIRouter()


@router.get("/items/{item_id}")
async def get_item_cached(item_id: int):
    """Get item with caching."""
    cache_key = f"item:{item_id}"

    # Try cache first
    cached = await get_cached(cache_key)
    if cached:
        return {"source": "cache", **cached}

    # Fetch from database
    item = await fetch_item_from_db(item_id)

    # Cache result
    await set_cached(cache_key, item, expire=300)

    return {"source": "db", **item}
```

## Alembic Migrations

### Setup

```bash
uv add alembic
alembic init alembic
```

### Configure Alembic (`alembic/env.py`)

```python
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your models
from database import Base
from models import User, Item  # Import all models

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### Create and Run Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add users and items tables"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```
