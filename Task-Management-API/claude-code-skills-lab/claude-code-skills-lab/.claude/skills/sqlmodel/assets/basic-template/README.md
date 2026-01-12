# FastAPI + SQLModel Basic Template

A minimal FastAPI application demonstrating SQLModel usage with CRUD operations.

## Setup

1. Initialize project with uv:
   ```bash
   uv init my-sqlmodel-app
   cd my-sqlmodel-app
   ```

2. Copy this template:
   ```bash
   cp -r path/to/template/* .
   ```

3. Add dependencies:
   ```bash
   uv add "fastapi[standard]" sqlmodel
   ```

4. Run the application:
   ```bash
   uv run fastapi dev main.py
   ```

5. Access the API:
   - API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Project Structure

```
.
├── main.py          # FastAPI application entry point
├── database.py      # Database configuration and session management
├── models.py        # SQLModel models and schemas
├── routes.py        # API route handlers
└── requirements.txt # Python dependencies
```

## API Endpoints

- `POST /heroes/` - Create a new hero
- `GET /heroes/` - Get all heroes (with pagination)
- `GET /heroes/{id}` - Get a specific hero
- `PATCH /heroes/{id}` - Update a hero
- `DELETE /heroes/{id}` - Delete a hero

## Example Usage

```bash
# Create a hero
curl -X POST "http://localhost:8000/heroes/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Spider-Man", "secret_name": "Peter Parker", "age": 25}'

# Get all heroes
curl "http://localhost:8000/heroes/"

# Get hero by ID
curl "http://localhost:8000/heroes/1"

# Update hero
curl -X PATCH "http://localhost:8000/heroes/1" \
     -H "Content-Type: application/json" \
     -d '{"age": 26}'

# Delete hero
curl -X DELETE "http://localhost:8000/heroes/1"
```

## Database

By default, uses SQLite (`database.db` file). To use PostgreSQL or other databases:

1. Add database driver:
   ```bash
   # For PostgreSQL
   uv add asyncpg psycopg2-binary

   # For MySQL
   uv add aiomysql pymysql
   ```

2. Update `DATABASE_URL` in `database.py`

## Testing

```bash
# Add test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
uv run pytest
```
