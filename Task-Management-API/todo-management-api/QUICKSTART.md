# Quick Start Guide

Get your Todo Management API running in 5 minutes!

## Step 1: Verify Prerequisites

```bash
# Check Python version (need 3.11+)
python --version

# Check if PostgreSQL is installed
psql --version

# Verify uv is available
uv --version
```

## Step 2: Database Setup

**Option A: NeonDB (Easiest - No install needed!)**

1. Go to [NeonDB](https://neon.tech) and sign up (free)
2. Create a new project
3. Copy your connection string
4. See [NEONDB_SETUP.md](NEONDB_SETUP.md) for full guide

**Option B: Local PostgreSQL**

```bash
# Start PostgreSQL
# Windows: Start from Services or pgAdmin
# Mac: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Create database
createdb todo_db

# Or using psql:
psql -U postgres
CREATE DATABASE todo_db;
\q
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional - defaults work for local development)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_db
```

## Step 4: Run the Application

```bash
# Start in development mode with auto-reload
uv run fastapi dev main.py
```

The API is now running at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Step 5: Test It Out!

Open http://localhost:8000/docs in your browser and try creating a todo:

1. Click on **POST /todos/**
2. Click **Try it out**
3. Enter this JSON:
```json
{
  "title": "My first todo",
  "description": "Testing the API",
  "priority": "high"
}
```
4. Click **Execute**

You should get a 201 response with your created todo!

## Verify with Tests

```bash
# Run all tests
uv run pytest -v

# See test coverage
uv run pytest --cov=. --cov-report=html
```

All 22 tests should pass! ✅

## Next Steps

- Explore all endpoints at `/docs`
- Try filtering: `/todos/?status=todo&priority=high`
- Check summary stats: `/todos/summary`
- Read the full [README.md](README.md) for more details

## Common Issues

### Database Connection Error
```bash
# Make sure PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                 # Mac

# Check database exists
psql -U postgres -l | grep todo_db
```

### Port Already in Use
```bash
# Use a different port
uv run fastapi dev main.py --port 8001
```

### Import Errors
```bash
# Always use 'uv run'
uv run fastapi dev main.py  # ✓ Correct
python main.py               # ✗ Wrong
```

---

🎉 **You're all set!** Start building amazing todo features!
