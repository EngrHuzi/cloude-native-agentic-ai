# Todo Management API

A secure REST API for managing todo items built with **FastAPI**, **SQLModel**, and **PostgreSQL**. Features user authentication with Argon2 password hashing, JWT tokens, full CRUD operations, filtering, pagination, and comprehensive test coverage.

## Features

### 🔐 Security & Authentication
- **Argon2 Password Hashing**: Industry-leading password security
- **JWT Token Authentication**: Secure access and refresh tokens
- **User Isolation**: Each user can only access their own todos
- **Protected Endpoints**: All todo operations require authentication

### ✅ Todo Management
- **Complete CRUD Operations**: Create, Read, Update, Delete todos
- **Status Management**: Todo, In Progress, Completed
- **Priority Levels**: Low, Medium, High
- **Due Date Tracking**: Set and track due dates
- **Filtering**: Filter by status and priority
- **Pagination**: Efficient pagination for large datasets
- **Summary Statistics**: Get overview of all todos

### 🚀 Technical Features
- **PostgreSQL Database**: Production-ready with async support
- **Comprehensive Tests**: Full test coverage with pytest
- **Auto-generated API Docs**: Interactive Swagger UI and ReDoc

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL databases with Python type annotations
- **PostgreSQL**: Production database with asyncpg driver
- **pwdlib + Argon2**: Password hashing with the gold standard algorithm
- **python-jose**: JWT token generation and verification
- **Alembic**: Database migrations
- **Pytest**: Testing framework with async support
- **uv**: Fast Python package manager

## project demo https://www.loom.com/share/b82f8a37d00240969f5bc7767c40a13a?t=151

## Prerequisites

- Python 3.11+
- PostgreSQL 13+ **OR** NeonDB account (recommended - no local install needed!)
- uv (Python package manager)

## Quick Start

### 1. Clone and Setup

```bash
cd todo-management-api

# Dependencies are already installed if you followed the setup
# Otherwise, run:
# uv add "fastapi[standard]" sqlmodel asyncpg psycopg2-binary alembic
# uv add --dev pytest pytest-cov pytest-asyncio httpx aiosqlite
```

### 2. Database Setup

**Option A: NeonDB (Recommended - Easier!)**

1. Sign up at [NeonDB](https://neon.tech) (free tier available)
2. Create a project and copy your connection string
3. See [NEONDB_SETUP.md](NEONDB_SETUP.md) for detailed instructions

**Option B: Local PostgreSQL**

Install and start PostgreSQL, then create the database:

```bash
# Using PostgreSQL CLI
createdb todo_db

# Or using psql
psql -U postgres
CREATE DATABASE todo_db;
\q
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials

# For NeonDB (easier):
# DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# For Local PostgreSQL:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/todo_db
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uv run fastapi dev main.py

# Production mode
uv run fastapi run main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

All todo endpoints require authentication. See [AUTH_GUIDE.md](AUTH_GUIDE.md) for complete documentation.

### Quick Authentication Flow

1. **Register a new user:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "securepass123"}'
```

2. **Login to get tokens:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=securepass123"
```

3. **Use the access token in requests:**
```bash
curl -X GET "http://localhost:8000/todos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Note:** Access tokens expire after 30 minutes. Use refresh tokens to get new access tokens without re-login.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and get tokens | No |
| POST | `/auth/refresh` | Refresh access token | No |
| GET | `/auth/me` | Get current user info | Yes |

### Todos (All require authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/todos/` | Create a new todo |
| GET | `/todos/` | Get all todos (with filtering & pagination) |
| GET | `/todos/{id}` | Get a specific todo |
| PATCH | `/todos/{id}` | Update a todo |
| DELETE | `/todos/{id}` | Delete a todo |
| POST | `/todos/{id}/complete` | Mark todo as completed |
| GET | `/todos/summary` | Get summary statistics |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |

## API Usage Examples

**Note:** All todo endpoints require authentication. Get your token from `/auth/login` or `/auth/register` first.

### Create a Todo

```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README and API docs",
    "status": "todo",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59"
  }'
```

### Get All Todos

```bash
# Basic
curl "http://localhost:8000/todos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With filters
curl "http://localhost:8000/todos/?status=todo&priority=high" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With pagination
curl "http://localhost:8000/todos/?offset=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Todo by ID

```bash
curl "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update Todo

```bash
curl -X PATCH "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high"
  }'
```

### Complete Todo

```bash
curl -X POST "http://localhost:8000/todos/1/complete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Delete Todo

```bash
curl -X DELETE "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Summary

```bash
curl "http://localhost:8000/todos/summary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Running Tests

The project includes comprehensive test coverage using pytest.

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_todos.py

# Run specific test class
uv run pytest tests/test_todos.py::TestTodoCreation

# Run specific test
uv run pytest tests/test_todos.py::TestTodoCreation::test_create_todo
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

## Database Migrations

Using Alembic for database schema management:

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## Project Structure

```
todo-management-api/
├── main.py                 # FastAPI application entry point
├── models.py              # SQLModel database models and schemas
├── database.py            # Database configuration and session
├── routes.py              # API route handlers for todos
├── auth/                  # Authentication module
│   ├── __init__.py
│   ├── config.py         # Auth configuration settings
│   ├── security.py       # Password hashing and JWT functions
│   ├── schemas.py        # Auth-related schemas
│   ├── dependencies.py   # Auth dependencies
│   └── router.py         # Auth endpoints (register, login, etc.)
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures and configuration
│   └── test_todos.py     # Todo API tests
├── pytest.ini            # Pytest configuration
├── .env.example          # Example environment variables
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Project dependencies (managed by uv)
├── AUTH_GUIDE.md        # Complete authentication documentation
└── README.md            # This file
```

## Data Models

### User

```python
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00"
}
```

### Todo

```python
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the todo API",
  "status": "in_progress",  # todo | in_progress | completed
  "priority": "high",       # low | medium | high
  "due_date": "2024-12-31T23:59:59",
  "completed_at": null,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "user_id": 1              # Foreign key to user
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/todo_db` |
| `SECRET_KEY` | JWT secret key (generate with `openssl rand -hex 32`) | Required in production |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `DEBUG` | Enable debug mode | `True` |

## Development

### Code Quality

```bash
# Format code with black
uv run black .

# Lint with ruff
uv run ruff check .

# Type checking with mypy
uv run mypy .
```

### Adding Dependencies

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name
```

## Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Run application
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

For production, ensure:
1. **Generate a secure SECRET_KEY**: `openssl rand -hex 32`
2. Set `DEBUG=False` in environment
3. Use strong database credentials
4. Configure CORS appropriately in `main.py`
5. Set up proper logging
6. Use reverse proxy (nginx/caddy)
7. Enable HTTPS
8. Rotate SECRET_KEY periodically
9. Use secure password requirements
10. Implement rate limiting on auth endpoints

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d todo_db -c "SELECT 1"
```

### Import Errors

```bash
# Ensure you're using uv run
uv run python main.py  # Correct
python main.py          # May fail (wrong environment)
```

### Test Failures

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Run tests with more verbose output
uv run pytest -vv
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and commercial purposes.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review test cases in `tests/`
- Open an issue on GitHub

---

**Built with FastAPI, SQLModel, and PostgreSQL** 🚀
