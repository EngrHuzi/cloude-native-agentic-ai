# Docker Setup for Todo Management API

This guide will help you containerize and run the Todo Management API using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

Verify installation:
```bash
docker --version
docker compose version
```

## Quick Start

### 1. Setup Environment Variables

Copy the Docker environment file and configure it:

```bash
cp .env.docker .env
```

Edit `.env` and update the following:
- `POSTGRES_PASSWORD`: Set a strong password for PostgreSQL
- `SECRET_KEY`: Generate with `openssl rand -hex 32`

### 2. Build and Start Services

```bash
# Build and start all services (API + PostgreSQL)
docker compose up -d --build

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f postgres
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123!"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"
```

## Docker Commands Reference

### Managing Services

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down -v

# Restart a specific service
docker compose restart api

# View running services
docker compose ps
```

### Logs and Debugging

```bash
# View all logs
docker compose logs -f

# View API logs only
docker compose logs -f api

# View last 100 lines
docker compose logs --tail=100 api

# Execute commands in containers
docker compose exec api bash
docker compose exec postgres psql -U postgres -d todo_db
```

### Database Operations

```bash
# Access PostgreSQL CLI
docker compose exec postgres psql -U postgres -d todo_db

# Create database backup
docker compose exec postgres pg_dump -U postgres todo_db > backup.sql

# Restore database
docker compose exec -T postgres psql -U postgres -d todo_db < backup.sql

# View database tables
docker compose exec postgres psql -U postgres -d todo_db -c "\dt"
```

### Building and Testing

```bash
# Rebuild without cache
docker compose build --no-cache

# Build specific service
docker compose build api

# Validate compose file
docker compose config

# Run tests in container
docker compose exec api pytest
```

## Architecture

```
┌─────────────────────────────────────────┐
│          Docker Compose Stack           │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   API        │    │  PostgreSQL  │  │
│  │  (FastAPI)   │───▶│   Database   │  │
│  │  Port: 8000  │    │  Port: 5432  │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
│         └────────────────────┘          │
│           todo-network (bridge)         │
│                                         │
│  Volume: postgres_data (persistent)     │
└─────────────────────────────────────────┘
```

## Dockerfile Details

The multi-stage Dockerfile includes:

### Stage 1: Builder
- Base: `python:3.13-slim`
- Installs build dependencies (gcc, libpq-dev)
- Uses `uv` package manager for fast dependency installation
- Creates virtual environment with all dependencies

### Stage 2: Production
- Minimal runtime image
- Non-root user (`appuser`) for security
- Only runtime dependencies (libpq5)
- Health check configured
- 4 uvicorn workers for production

**Image Size**: ~160MB (optimized with multi-stage build)

## Security Features

- **Non-root user**: Application runs as `appuser` (UID 1000)
- **No hardcoded secrets**: All secrets from environment variables
- **Health checks**: Both API and database monitored
- **Network isolation**: Services on private `todo-network`
- **Minimal attack surface**: Alpine-based PostgreSQL, slim Python image

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | Database name | `todo_db` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `API_PORT` | API port | `8000` |
| `SECRET_KEY` | JWT secret key | *Required* |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `DEBUG` | Debug mode | `False` |

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs api

# Check container status
docker compose ps

# Restart services
docker compose restart
```

### Database Connection Issues

```bash
# Verify PostgreSQL is healthy
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection manually
docker compose exec postgres pg_isready -U postgres

# Verify environment variables
docker compose exec api env | grep DATABASE_URL
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -ti:8000

# Kill process (Unix/Mac)
lsof -ti:8000 | xargs kill

# Or change port in .env
API_PORT=8080
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker compose up -d --build

# Or rebuild without cache
docker compose build --no-cache
docker compose up -d
```

## Production Deployment

### Option 1: Docker Compose on VPS

```bash
# On your server
git clone <your-repo>
cd todo-management-api

# Setup environment
cp .env.docker .env
nano .env  # Edit with production values

# Start services
docker compose up -d

# Setup reverse proxy (Nginx)
# See references/production-deployment.md
```

### Option 2: Cloud Platforms

- **Railway**: Connect GitHub repo, auto-detects Dockerfile
- **Render**: Use `render.yaml` blueprint (create from docker-compose.yaml)
- **Fly.io**: `flyctl launch && flyctl deploy`
- **AWS ECS**: Use AWS CLI with docker-compose.yaml
- **Google Cloud Run**: `gcloud run deploy --source .`

See `.claude/skills/docker/references/production-deployment.md` for detailed guides.

## Development Mode

To enable hot-reloading for development:

1. Uncomment volume mount in `docker-compose.yaml`:
```yaml
api:
  volumes:
    - ./:/app  # Uncomment this line
```

2. Update Dockerfile CMD for development:
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

3. Rebuild and restart:
```bash
docker compose up -d --build
```

## Cleanup

```bash
# Stop and remove containers
docker compose down

# Remove containers and volumes
docker compose down -v

# Remove images
docker rmi todo-management-api-api

# Full cleanup (all Docker resources)
docker system prune -a --volumes
```

## Next Steps

- Add Redis for caching (see `.claude/skills/docker/assets/basic-template/fastapi-postgres-redis`)
- Setup CI/CD pipeline
- Configure monitoring and logging
- Add Nginx reverse proxy
- Setup SSL/TLS certificates
- Implement database migrations with Alembic

## Support

For issues and questions:
- Check logs: `docker compose logs -f`
- Validate config: `docker compose config`
- Review Docker skill: `.claude/skills/docker/SKILL.md`
