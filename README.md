# Todo Management API

[![Docker Hub](https://img.shields.io/docker/v/muhammadhuzaifa366/todo-management-api?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/muhammadhuzaifa366/todo-management-api)
[![Docker Image Size](https://img.shields.io/docker/image-size/muhammadhuzaifa366/todo-management-api/latest)](https://hub.docker.com/r/muhammadhuzaifa366/todo-management-api)
[![Docker Pulls](https://img.shields.io/docker/pulls/muhammadhuzaifa366/todo-management-api)](https://hub.docker.com/r/muhammadhuzaifa366/todo-management-api)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)](https://kubernetes.io)

A secure REST API for managing todo items built with **FastAPI**, **SQLModel**, and **PostgreSQL**. Features user authentication with Argon2 password hashing, JWT tokens, full CRUD operations, filtering, pagination, and comprehensive test coverage.

## 🐳 Quick Start with Docker Hub

Pull and run the pre-built image from Docker Hub:

```bash
# Pull the latest image
docker pull muhammadhuzaifa366/todo-management-api:latest

# Run with Docker Compose (Recommended)
curl -O https://raw.githubusercontent.com/yourusername/todo-management-api/main/docker-compose.yaml
docker compose up -d

# Or run standalone (requires external PostgreSQL)
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  muhammadhuzaifa366/todo-management-api:latest
```

**🌐 Access the API**: http://localhost:8000/docs

---

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
- **Docker Ready**: Production-optimized containers with multi-stage builds
- **Kubernetes Ready**: Deploy with K8s manifests, HPA, and persistent storage
- **Comprehensive Tests**: Full test coverage with pytest
- **Auto-generated API Docs**: Interactive Swagger UI and ReDoc
- **Easy Deployment**: Deploy to any cloud platform with Docker or Kubernetes

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL databases with Python type annotations
- **PostgreSQL**: Production database with asyncpg driver
- **pwdlib + Argon2**: Password hashing with the gold standard algorithm
- **python-jose**: JWT token generation and verification
- **Alembic**: Database migrations
- **Pytest**: Testing framework with async support
- **uv**: Fast Python package manager
- **Docker**: Containerization with multi-stage builds
- **Docker Compose**: Multi-container orchestration
- **Kubernetes**: Container orchestration with K8s and Kustomize

## project demo https://www.loom.com/share/b82f8a37d00240969f5bc7767c40a13a?t=151

## Prerequisites

### Option 1: Docker (Recommended - Easiest!)
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+

### Option 2: Kubernetes (Cloud-Native)
- Kubernetes cluster (Docker Desktop K8s, Minikube, Kind, or cloud K8s)
- kubectl CLI installed
- [Optional] Kustomize for manifest management

### Option 3: Local Development
- Python 3.11+
- PostgreSQL 13+ **OR** NeonDB account (recommended - no local install needed!)
- uv (Python package manager)

## Quick Start

### 🐳 Option A: Docker (Recommended)

The fastest way to get started! Everything runs in containers - no local Python or PostgreSQL installation needed.

#### Method 1: Pull from Docker Hub (Fastest)

```bash
# Create a docker-compose.yaml file
cat > docker-compose.yaml << 'EOF'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: todo_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d todo_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: muhammadhuzaifa366/todo-management-api:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/todo_db
      SECRET_KEY: change-this-to-a-secure-random-key-in-production
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      DEBUG: False
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Start services
docker compose up -d

# View logs
docker compose logs -f
```

#### Method 2: Build from Source

```bash
# Navigate to project directory
cd todo-management-api

# Copy Docker environment file
cp .env.docker .env

# (Optional) Edit .env to customize settings
# nano .env

# Build and start all services (API + PostgreSQL)
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**That's it!** The API is now running at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**📖 For detailed Docker documentation, see [DOCKER_README.md](DOCKER_README.md)**

---

### ☸️ Option C: Kubernetes (Cloud-Native Deployment)

Deploy to any Kubernetes cluster with auto-scaling and persistent storage.

**Prerequisites:**
```bash
# Verify cluster connection
kubectl cluster-info

# Enable Kubernetes in Docker Desktop
# Settings → Kubernetes → Enable Kubernetes → Apply & Restart
```

#### Quick Deploy with Kustomize

```bash
# 1. Navigate to project directory
cd todo-management-api

# 2. Create namespace
kubectl create namespace todo-api

# 3. Update secrets (IMPORTANT!)
# Edit k8s/secrets.yaml and update:
# - database-url: Your PostgreSQL connection string
# - secret-key: Generate with: openssl rand -hex 32

# 4. Deploy all resources
kubectl apply -k k8s/

# 5. Wait for pods to be ready
kubectl wait --for=condition=ready --timeout=120s pod -l app=todo-api -n todo-api

# 6. Verify deployment
kubectl get all -n todo-api
```

#### Access the Application

**Option 1: NodePort (Docker Desktop)**
```bash
# Access via NodePort
curl http://localhost:30080/health

# Open in browser
# http://localhost:30080/docs
```

**Option 2: Port Forwarding**
```bash
# Forward local port to service
kubectl port-forward -n todo-api service/todo-api 8000:8000

# Access API
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

#### Kubernetes Features

**Deployment Configuration:**
- ✅ **2 replicas** with auto-scaling (2-10 pods via HPA)
- ✅ **Resource limits**: CPU 100m-500m, Memory 128Mi-512Mi
- ✅ **Health probes**: Liveness and readiness checks
- ✅ **Rolling updates**: Zero-downtime deployments
- ✅ **PostgreSQL**: Persistent volumes with 1Gi storage

**Auto-Scaling:**
- Scales based on CPU (70%) and Memory (80%) usage
- Minimum 2 replicas, maximum 10 replicas
- Stabilization windows for smooth scaling

**Monitoring & Management:**
```bash
# View all resources
kubectl get all -n todo-api

# Check HPA status
kubectl get hpa -n todo-api -w

# View logs
kubectl logs -l app=todo-api -n todo-api -f

# Scale manually
kubectl scale deployment todo-api --replicas=4 -n todo-api

# Rollout restart
kubectl rollout restart deployment todo-api -n todo-api
```

#### Included Kubernetes Files

```
k8s/
├── deployment.yaml          # API deployment with HPA
├── service.yaml             # NodePort service (30080)
├── secrets.yaml             # Database & JWT secrets
├── postgres-deployment.yaml  # PostgreSQL database
├── kustomization.yaml       # Kustomize config
└── DEPLOYMENT.md            # Complete deployment guide
```

#### Troubleshooting Kubernetes

**Pods not starting:**
```bash
# Check pod status
kubectl get pods -n todo-api

# Describe pod for events
kubectl describe pod <pod-name> -n todo-api

# Check logs
kubectl logs <pod-name> -n todo-api --tail=50

# Check previous container logs
kubectl logs <pod-name> -n todo-api --previous=true
```

**Database connection issues:**
```bash
# Verify PostgreSQL is running
kubectl get pods -l app=postgres -n todo-api

# Test database connection
kubectl exec -it <postgres-pod> -n todo-api -- psql -U postgres -d todo_db
```

**Cleanup:**
```bash
# Delete all resources
kubectl delete -k k8s/

# Or delete namespace
kubectl delete namespace todo-api
```

**📖 For detailed Kubernetes documentation, see [k8s/DEPLOYMENT.md](k8s/DEPLOYMENT.md)**

---

### 💻 Option B: Local Development

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
├── k8s/                   # Kubernetes manifests
│   ├── deployment.yaml   # API deployment with HPA
│   ├── service.yaml      # NodePort service
│   ├── secrets.yaml      # Database & JWT secrets
│   ├── postgres-deployment.yaml  # PostgreSQL deployment
│   ├── kustomization.yaml  # Kustomize config
│   └── DEPLOYMENT.md     # Kubernetes deployment guide
├── Dockerfile            # Multi-stage production Docker build
├── docker-compose.yaml   # Docker Compose configuration (API + PostgreSQL)
├── .dockerignore        # Docker build context exclusions
├── pytest.ini            # Pytest configuration
├── .env.example          # Example environment variables (local)
├── .env.docker           # Example environment variables (Docker)
├── .env                  # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Project dependencies (managed by uv)
├── uv.lock              # Dependency lock file
├── AUTH_GUIDE.md        # Complete authentication documentation
├── DOCKER_README.md     # Complete Docker setup guide
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

### 🐳 Docker Deployment (Production-Ready)

The project includes production-ready Docker configuration with multi-stage builds, security hardening, and PostgreSQL database.

**Docker Hub Image**: `muhammadhuzaifa366/todo-management-api`

#### Available Tags
- `latest` - Latest stable version
- `v1.0.0` - Specific version (recommended for production)

#### Files Included
- `Dockerfile` - Multi-stage production build (~160MB optimized image)
- `docker-compose.yaml` - Full stack with API + PostgreSQL
- `.dockerignore` - Optimized build context
- `.env.docker` - Environment template for Docker
- `DOCKER_README.md` - Complete Docker documentation

#### Quick Deploy Option 1: Use Pre-built Image (Recommended)

```bash
# 1. Create docker-compose.yaml with the public image
cat > docker-compose.yaml << 'EOF'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-strong-password-here}
      POSTGRES_DB: todo_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d todo_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: muhammadhuzaifa366/todo-management-api:v1.0.0
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD:-strong-password-here}@postgres:5432/todo_db
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      REFRESH_TOKEN_EXPIRE_DAYS: 7
      DEBUG: False
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# 2. Create .env file with secure credentials
cat > .env << 'EOF'
POSTGRES_PASSWORD=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)
EOF

# Or manually set:
echo "POSTGRES_PASSWORD=your-strong-password" > .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 3. Start services
docker compose up -d

# 4. Verify
docker compose ps
curl http://localhost:8000/health
```

#### Quick Deploy Option 2: Build from Source

```bash
# 1. Copy environment file
cp .env.docker .env

# 2. Generate secure SECRET_KEY
openssl rand -hex 32
# Copy the output and update SECRET_KEY in .env

# 3. Edit .env with production values
nano .env
# Update: POSTGRES_PASSWORD, SECRET_KEY, DEBUG=False

# 4. Build and start services
docker compose up -d --build

# 5. Verify services are running
docker compose ps
docker compose logs -f

# 6. Test API
curl http://localhost:8000/health
```

#### Docker Features
- **Multi-stage build**: Optimized image size (builder + production)
- **Security**: Non-root user, minimal attack surface
- **Health checks**: Both API and database monitored
- **PostgreSQL 16**: With persistent volumes
- **Auto-restart**: Containers restart on failure
- **Network isolation**: Services on private network

#### Production Deployment Platforms

**1. Ubuntu/Linux Server (Using Docker Hub Image)**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Create deployment directory
mkdir todo-api && cd todo-api

# Create docker-compose.yaml
cat > docker-compose.yaml << 'EOF'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: todo_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  api:
    image: muhammadhuzaifa366/todo-management-api:v1.0.0
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/todo_db
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Create .env file
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" > .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Deploy
docker compose up -d
```

**2. Cloud Platforms**

**Using Pre-built Docker Hub Image:**
- **Railway**: Use Docker image `muhammadhuzaifa366/todo-management-api:v1.0.0`
- **Render**: Use Docker image in Web Service settings
- **Fly.io**:
  ```bash
  flyctl launch --image muhammadhuzaifa366/todo-management-api:v1.0.0
  flyctl deploy
  ```
- **AWS ECS**: Reference `muhammadhuzaifa366/todo-management-api:v1.0.0` in task definition
- **Google Cloud Run**:
  ```bash
  gcloud run deploy todo-api \
    --image muhammadhuzaifa366/todo-management-api:v1.0.0 \
    --platform managed
  ```
- **DigitalOcean App Platform**: Use Docker Hub image in app spec

**Building from Source:**
- Clone repository and use provided Dockerfile
- All platforms support custom Dockerfile builds

### ☸️ Kubernetes Deployment (Cloud-Native)

The project includes production-ready Kubernetes manifests for deploying to any K8s cluster.

#### Kubernetes Features
- **Auto-scaling**: HorizontalPodAutoscaler (2-10 pods based on CPU/Memory)
- **High Availability**: 2 replicas with rolling updates
- **Persistent Storage**: PostgreSQL with PersistentVolumeClaims
- **Health Monitoring**: Liveness and readiness probes
- **Resource Management**: CPU and memory requests/limits
- **NodePort Service**: Access via localhost:30080 (Docker Desktop)

#### Quick Deploy

```bash
# Create namespace
kubectl create namespace todo-api

# Deploy with Kustomize
kubectl apply -k k8s/

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=todo-api -n todo-api

# Access API
kubectl port-forward -n todo-api service/todo-api 8000:8000
# Or via NodePort: http://localhost:30080/docs
```

#### Files Included
- `k8s/deployment.yaml` - Deployment + HPA configuration
- `k8s/service.yaml` - NodePort service (port 30080)
- `k8s/secrets.yaml` - Kubernetes secrets template
- `k8s/postgres-deployment.yaml` - PostgreSQL with PVC
- `k8s/kustomization.yaml` - Kustomize configuration
- `k8s/DEPLOYMENT.md` - Complete deployment guide

**📖 For detailed Kubernetes documentation, see [k8s/DEPLOYMENT.md](k8s/DEPLOYMENT.md)**

---

### Environment Setup for Production

**Critical Security Steps:**

1. **Generate secure SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```

2. **Update .env file**
   ```bash
   SECRET_KEY=<generated-key-from-step-1>
   POSTGRES_PASSWORD=<strong-unique-password>
   DEBUG=False
   ```

3. **Database Configuration**
   - Use strong passwords (min 16 characters)
   - Enable SSL/TLS for database connections
   - Regular backups (automated)

4. **Application Security**
   - Configure CORS appropriately in `main.py`
   - Set up proper logging
   - Use reverse proxy (nginx/caddy) with rate limiting
   - Enable HTTPS with valid SSL certificates
   - Implement rate limiting on auth endpoints

5. **Monitoring & Maintenance**
   - Set up health check monitoring
   - Configure log aggregation
   - Rotate SECRET_KEY periodically
   - Keep dependencies updated
   - Regular security audits

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

### Docker Issues

```bash
# View container logs
docker compose logs -f api
docker compose logs -f postgres

# Restart services
docker compose restart

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d

# Check container status
docker compose ps

# Access container shell
docker compose exec api bash
docker compose exec postgres psql -U postgres -d todo_db

# Port already in use
docker compose down
# Or change port in .env: API_PORT=8080

# Clean up everything
docker compose down -v  # Warning: Deletes database data!
docker system prune -a
```

**For detailed Docker troubleshooting, see [DOCKER_README.md](DOCKER_README.md)**

### Kubernetes Issues

```bash
# Pods not starting
kubectl get pods -n todo-api
kubectl describe pod <pod-name> -n todo-api
kubectl logs <pod-name> -n todo-api --previous=true

# Service not accessible
kubectl get endpoints todo-api -n todo-api
kubectl port-forward -n todo-api service/todo-api 8000:8000

# HPA not scaling
kubectl get hpa -n todo-api
kubectl describe hpa todo-api-hpa -n todo-api

# Delete all resources
kubectl delete namespace todo-api
```

**For detailed Kubernetes troubleshooting, see [k8s/DEPLOYMENT.md](k8s/DEPLOYMENT.md)**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## For Maintainers: Updating Docker Hub

When you make changes and want to publish a new version to Docker Hub:

```bash
# 1. Make your code changes and test locally
docker compose build
docker compose up -d
# Test thoroughly...

# 2. Login to Docker Hub (if not already logged in)
docker login

# 3. Tag the new version
VERSION="v1.0.1"  # Increment version number
docker tag todo-management-api-api:latest muhammadhuzaifa366/todo-management-api:$VERSION
docker tag todo-management-api-api:latest muhammadhuzaifa366/todo-management-api:latest

# 4. Push to Docker Hub
docker push muhammadhuzaifa366/todo-management-api:$VERSION
docker push muhammadhuzaifa366/todo-management-api:latest

# 5. Update README.md
# - Update version numbers in deployment examples
# - Update CHANGELOG if you have one
```

**Version Tagging Convention:**
- `latest` - Always points to the most recent stable release
- `v1.0.0` - Semantic versioning (MAJOR.MINOR.PATCH)
  - MAJOR: Breaking changes
  - MINOR: New features, backwards compatible
  - PATCH: Bug fixes, backwards compatible

**GitHub Actions (Optional):**
You can automate this process by setting up GitHub Actions to automatically build and push to Docker Hub on new releases.

## License

MIT License - feel free to use this project for learning and commercial purposes.

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review test cases in `tests/`
- Open an issue on GitHub

---

**Built with FastAPI, SQLModel, PostgreSQL, and Kubernetes** 🚀

**Available on Docker Hub**: [muhammadhuzaifa366/todo-management-api](https://hub.docker.com/r/muhammadhuzaifa366/todo-management-api)

**Kubernetes Ready**: Deploy with `kubectl apply -k k8s/` ☸️
