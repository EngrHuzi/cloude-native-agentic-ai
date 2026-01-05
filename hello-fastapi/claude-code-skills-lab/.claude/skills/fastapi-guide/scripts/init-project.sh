#!/usr/bin/env bash
# Initialize a new FastAPI project with uv

set -e

PROJECT_NAME="${1:-my-fastapi-app}"
PROJECT_TYPE="${2:-basic}"  # basic, with-db, with-auth, full

echo "Creating FastAPI project: $PROJECT_NAME (type: $PROJECT_TYPE)"

# Create project directory
uv init "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Add FastAPI with standard dependencies
echo "Adding FastAPI and dependencies..."
uv add "fastapi[standard]"

# Add dependencies based on project type
case "$PROJECT_TYPE" in
  "with-db")
    echo "Adding database dependencies..."
    uv add sqlalchemy alembic asyncpg psycopg2-binary
    ;;
  "with-auth")
    echo "Adding authentication dependencies..."
    uv add "python-jose[cryptography]" passlib python-multipart bcrypt
    ;;
  "full")
    echo "Adding all dependencies..."
    uv add sqlalchemy alembic asyncpg psycopg2-binary
    uv add "python-jose[cryptography]" passlib python-multipart bcrypt
    uv add redis motor pytest httpx pytest-asyncio
    ;;
esac

# Add development dependencies
echo "Adding development dependencies..."
uv add --dev pytest pytest-asyncio httpx black ruff mypy

echo "Project $PROJECT_NAME created successfully!"
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  uv run fastapi dev main.py"
