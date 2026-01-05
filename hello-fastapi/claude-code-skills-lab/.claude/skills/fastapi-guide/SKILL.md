---
name: fastapi-guide
description: Complete zero-to-hero FastAPI development guide using modern Python with uv package manager. Covers project initialization with 'uv init', dependency management with 'uv add', building APIs from basic CRUD to advanced features (database integration, authentication, middleware, testing, deployment). Use when building FastAPI applications, setting up new FastAPI projects, adding features like database/auth/testing, or deploying FastAPI apps. NOT for other Python frameworks.
---

# FastAPI Development Guide

Complete guide for building FastAPI applications with modern Python tooling using `uv` package manager.

## When to Use This Skill

Use this skill when:
- Creating a new FastAPI project from scratch
- Adding database integration (SQL, MongoDB, Redis)
- Implementing authentication and authorization
- Setting up testing infrastructure
- Deploying FastAPI applications
- Adding middleware, WebSockets, or background tasks

## Quick Start

### 1. Create New Project

Use the initialization script:

```bash
bash scripts/init-project.sh my-api basic
```

Options:
- `basic` - Simple API with in-memory storage
- `with-db` - Includes SQLAlchemy and database setup
- `with-auth` - Includes authentication dependencies
- `full` - All features (database + auth + Redis + testing)

Or use the basic template:

```bash
# Copy basic template
cp -r assets/basic-template/* my-api/
cd my-api

# Initialize with uv
uv init
uv add "fastapi[standard]"

# Run
uv run fastapi dev main.py
```

### 2. Package Management with uv

```bash
# Add dependencies
uv add package-name

# Add dev dependencies
uv add --dev pytest black ruff

# Add database dependencies
uv add sqlalchemy alembic asyncpg

# Add authentication dependencies
uv add "python-jose[cryptography]" passlib bcrypt

# Run commands
uv run fastapi dev main.py
uv run pytest
```

### 3. Generate CRUD Endpoints

```bash
python scripts/generate-crud.py User --fields name:str email:str age:int
```

This creates:
- `user_router/schemas.py` - Pydantic models
- `user_router/router.py` - CRUD endpoints
- Ready to integrate into your app

## Progressive Feature Addition

### Level 1: Basic API (✓ You start here)

Simple CRUD operations with Pydantic validation:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

**Next step:** Add database integration (Level 2)

### Level 2: Database Integration

**Quick reference:** See [references/databases.md](references/databases.md)

Key sections:
- **SQLAlchemy (Async)** - Full async PostgreSQL/SQLite setup with models, CRUD operations
- **MongoDB with Motor** - Async MongoDB integration
- **Redis Caching** - Cache layer implementation
- **Alembic Migrations** - Database migration management

Common pattern:

```bash
# Add dependencies
uv add sqlalchemy asyncpg alembic

# Read database reference for setup
# See references/databases.md - SQLAlchemy section

# Run migrations
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

**Next step:** Add authentication (Level 3)

### Level 3: Authentication & Authorization

**Quick reference:** See [references/authentication.md](references/authentication.md)

Key sections:
- **JWT Token Authentication** - OAuth2 + Bearer token setup
- **Password Hashing** - bcrypt implementation
- **Role-Based Access Control** - Permissions and roles
- **API Key Authentication** - API key validation

Common pattern:

```bash
# Add dependencies
uv add "python-jose[cryptography]" passlib bcrypt python-multipart

# Read authentication reference
# See references/authentication.md - JWT section
```

**Next step:** Add testing (Level 4)

### Level 4: Testing

**Quick reference:** See [references/testing.md](references/testing.md)

Key sections:
- **Basic Testing** - TestClient setup
- **Async Testing** - AsyncClient with database
- **Authentication Testing** - Testing protected endpoints
- **Test Coverage** - pytest-cov configuration

Common pattern:

```bash
# Add test dependencies
uv add --dev pytest pytest-asyncio httpx pytest-cov

# Read testing reference
# See references/testing.md

# Run tests
uv run pytest
uv run pytest --cov=app --cov-report=html
```

**Next step:** Deploy (Level 5)

### Level 5: Deployment

**Quick reference:** See [references/deployment.md](references/deployment.md)

Key sections:
- **Docker** - Containerization with multi-stage builds
- **Kubernetes** - K8s manifests and configuration
- **Cloud Platforms** - AWS (ECS/Lambda), GCP (Cloud Run), Azure
- **Traditional VPS** - systemd + nginx setup

Common pattern:

```bash
# Create Dockerfile
# See references/deployment.md - Docker section

# Build and run
docker build -t my-api .
docker run -p 8000:8000 my-api
```

## Reference Files

Load these files as needed for detailed implementation:

- **[databases.md](references/databases.md)** (3.4k words) - Database integration patterns
  - Read when: Setting up database, adding models, implementing CRUD
  - Sections: SQLAlchemy, MongoDB, Redis, Alembic migrations

- **[authentication.md](references/authentication.md)** (2.8k words) - Auth implementation
  - Read when: Adding login, protecting endpoints, implementing RBAC
  - Sections: JWT, Password hashing, OAuth2, API keys, RBAC

- **[deployment.md](references/deployment.md)** (2.6k words) - Deployment strategies
  - Read when: Deploying to production, containerizing, setting up CI/CD
  - Sections: Docker, Kubernetes, AWS, GCP, Azure, VPS

- **[testing.md](references/testing.md)** (2.2k words) - Testing strategies
  - Read when: Writing tests, setting up CI, testing auth/database
  - Sections: pytest setup, async tests, fixtures, mocking, coverage

## Common Workflows

### Creating a Complete API from Scratch

1. Initialize project:
   ```bash
   bash scripts/init-project.sh my-blog-api full
   cd my-blog-api
   ```

2. Set up database (read references/databases.md):
   - Configure database URL in .env
   - Create models in models.py
   - Set up Alembic migrations

3. Add authentication (read references/authentication.md):
   - Implement user registration/login
   - Add JWT token generation
   - Protect endpoints with dependencies

4. Generate CRUD endpoints:
   ```bash
   python scripts/generate-crud.py Post --fields title:str content:str author_id:int
   python scripts/generate-crud.py Comment --fields content:str post_id:int user_id:int
   ```

5. Set up testing (read references/testing.md):
   - Create test database fixtures
   - Write endpoint tests
   - Add authentication tests

6. Deploy (read references/deployment.md):
   - Create Dockerfile
   - Set up docker-compose for local dev
   - Deploy to cloud platform

### Adding Database to Existing API

1. Add dependencies:
   ```bash
   uv add sqlalchemy asyncpg alembic
   ```

2. Read references/databases.md - SQLAlchemy section

3. Follow the setup pattern:
   - Create `database.py` with async engine
   - Create `models.py` with SQLAlchemy models
   - Create `crud.py` with async CRUD operations
   - Update routers to use `Depends(get_db)`

4. Initialize Alembic:
   ```bash
   alembic init alembic
   # Configure as shown in references/databases.md
   alembic revision --autogenerate -m "Initial"
   alembic upgrade head
   ```

### Adding Authentication to Existing API

1. Add dependencies:
   ```bash
   uv add "python-jose[cryptography]" passlib bcrypt python-multipart
   ```

2. Read references/authentication.md - JWT section

3. Create auth module structure:
   ```
   auth/
   ├── __init__.py
   ├── config.py      # Settings
   ├── security.py    # Password hashing, JWT creation
   ├── schemas.py     # Pydantic models
   ├── dependencies.py # get_current_user
   └── router.py      # /auth endpoints
   ```

4. Protect endpoints:
   ```python
   from auth.dependencies import get_current_user

   @app.get("/protected")
   async def protected(user = Depends(get_current_user)):
       return {"user": user.username}
   ```

## Best Practices

### Project Structure

```
my-api/
├── main.py              # App entry point
├── database.py          # DB configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py              # Database operations
├── routers/             # API routers
│   ├── users.py
│   ├── items.py
│   └── auth.py
├── auth/                # Authentication module
│   ├── config.py
│   ├── security.py
│   └── dependencies.py
├── tests/               # Test files
│   ├── conftest.py
│   ├── test_users.py
│   └── test_auth.py
├── alembic/             # Database migrations
├── .env                 # Environment variables
├── pyproject.toml       # Dependencies
└── Dockerfile           # Container definition
```

### Key Principles

1. **Use uv** for package management (NOT pip)
2. **Async all the way** - Use async/await for database and I/O operations
3. **Type hints** - Leverage Pydantic for validation and documentation
4. **Separate concerns** - Keep routers, models, schemas, and CRUD operations separate
5. **Environment variables** - Use .env files for configuration
6. **Test everything** - Write tests with pytest and pytest-asyncio
7. **Security first** - Hash passwords, validate tokens, use HTTPS

### Common Commands

```bash
# Development
uv run fastapi dev main.py

# Production
uv run fastapi run main.py

# Testing
uv run pytest
uv run pytest -v --cov=app

# Migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1

# Code quality
uv run black .
uv run ruff check .
uv run mypy .

# Docker
docker build -t api .
docker run -p 8000:8000 api
docker-compose up -d
```

## Troubleshooting

### "ModuleNotFoundError" when running app
- Ensure you're using `uv run` prefix
- Check dependencies: `uv add fastapi`

### Database connection errors
- Verify DATABASE_URL in .env
- Check database is running (postgres, mongodb)
- See references/databases.md for connection strings

### Authentication not working
- Verify SECRET_KEY is set
- Check token expiration
- See references/authentication.md for debugging

### Tests failing
- Ensure using test database (not production)
- Check async fixtures setup
- See references/testing.md for test database configuration

## Additional Resources

- **Scripts** - Ready-to-use helper scripts in `scripts/`
  - `init-project.sh` - Initialize new FastAPI project
  - `generate-crud.py` - Generate CRUD endpoints

- **Templates** - Project templates in `assets/`
  - `basic-template/` - Minimal FastAPI app

For detailed information on any topic, read the corresponding reference file.
