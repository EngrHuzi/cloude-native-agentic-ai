# FastAPI Basic Template

A minimal FastAPI application template to get you started quickly.

## Setup

1. Initialize project with uv:
```bash
uv init my-fastapi-app
cd my-fastapi-app
```

2. Copy this template:
```bash
cp path/to/template/* .
```

3. Add dependencies:
```bash
uv add "fastapi[standard]"
```

4. Run the application:
```bash
uv run fastapi dev main.py
```

## Features

- CRUD operations for items
- Automatic API documentation
- Input validation with Pydantic
- Health check endpoint

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API docs (Swagger UI)
- `GET /redoc` - Alternative API docs (ReDoc)
- `POST /items/` - Create item
- `GET /items/` - List items
- `GET /items/{item_id}` - Get item by ID
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

## Next Steps

- Add database integration (see references/databases.md)
- Implement authentication (see references/authentication.md)
- Add testing (see references/testing.md)
- Deploy your app (see references/deployment.md)
