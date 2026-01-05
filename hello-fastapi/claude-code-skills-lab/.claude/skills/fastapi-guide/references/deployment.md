# Deployment Guide

Complete deployment guide for FastAPI applications across different platforms.

## Table of Contents

- Docker Containerization
- Docker Compose for Development
- Kubernetes Deployment
- AWS Deployment (ECS, Lambda, EC2)
- GCP Deployment (Cloud Run, App Engine)
- Azure Deployment
- Traditional VPS/Server Setup

## Docker Containerization

### Dockerfile

```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-stage Build (Production)

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Runtime stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
*.db
*.sqlite
.env
.env.*
!.env.example
```

### Build and Run

```bash
# Build image
docker build -t fastapi-app:latest .

# Run container
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  fastapi-app:latest

# View logs
docker logs -f fastapi-app

# Stop container
docker stop fastapi-app
```

## Docker Compose for Development

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key}
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    command: uv run fastapi dev main.py --host 0.0.0.0 --port 8000

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - db

volumes:
  postgres_data:
  redis_data:
```

### Usage

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Run migrations
docker-compose exec app alembic upgrade head

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Kubernetes Deployment

### Deployment (`k8s/deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  labels:
    app: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: secret-key
        - name: REDIS_URL
          value: redis://redis-service:6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service (`k8s/service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: LoadBalancer
  selector:
    app: fastapi-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### ConfigMap (`k8s/configmap.yaml`)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "info"
```

### Secrets (`k8s/secrets.yaml`)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-secrets
type: Opaque
stringData:
  database-url: postgresql+asyncpg://user:password@postgres:5432/dbname
  secret-key: your-very-secret-key
```

### Ingress (`k8s/ingress.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: fastapi-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/fastapi-app

# Scale deployment
kubectl scale deployment/fastapi-app --replicas=5

# Update image
kubectl set image deployment/fastapi-app fastapi-app=your-registry/fastapi-app:v2
```

## AWS Deployment

### AWS ECS with Fargate

**task-definition.json:**

```json
{
  "family": "fastapi-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "fastapi-app",
      "image": "your-ecr-repo/fastapi-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fastapi-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Deploy:**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-ecr-repo
docker build -t fastapi-app .
docker tag fastapi-app:latest your-ecr-repo/fastapi-app:latest
docker push your-ecr-repo/fastapi-app:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create or update service
aws ecs create-service \
  --cluster your-cluster \
  --service-name fastapi-service \
  --task-definition fastapi-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### AWS Lambda with Mangum

**Install Mangum:**

```bash
uv add mangum
```

**lambda_handler.py:**

```python
from mangum import Mangum
from main import app

# Lambda handler
handler = Mangum(app)
```

**Deploy with AWS SAM:**

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  FastAPIFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.handler
      Runtime: python3.12
      MemorySize: 512
      Timeout: 30
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseURL
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
```

```bash
sam build
sam deploy --guided
```

## GCP Deployment

### Cloud Run

**Deploy:**

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/fastapi-app

# Deploy to Cloud Run
gcloud run deploy fastapi-app \
  --image gcr.io/PROJECT_ID/fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://... \
  --set-secrets SECRET_KEY=secret-key:latest
```

### App Engine

**app.yaml:**

```yaml
runtime: python312
entrypoint: uv run uvicorn main:app --host 0.0.0.0 --port $PORT

env_variables:
  ENVIRONMENT: "production"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

**Deploy:**

```bash
gcloud app deploy
```

## Azure Deployment

### Azure Container Apps

```bash
# Create resource group
az group create --name fastapi-rg --location eastus

# Create container app environment
az containerapp env create \
  --name fastapi-env \
  --resource-group fastapi-rg \
  --location eastus

# Deploy container app
az containerapp create \
  --name fastapi-app \
  --resource-group fastapi-rg \
  --environment fastapi-env \
  --image your-registry/fastapi-app:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL=secretref:database-url SECRET_KEY=secretref:secret-key \
  --min-replicas 1 \
  --max-replicas 10
```

## Traditional VPS/Server Setup

### Systemd Service

**fastapi.service:**

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/fastapi-app
Environment="PATH=/var/www/fastapi-app/.venv/bin"
ExecStart=/var/www/fastapi-app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Setup:**

```bash
# Copy service file
sudo cp fastapi.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable fastapi
sudo systemctl start fastapi

# Check status
sudo systemctl status fastapi

# View logs
sudo journalctl -u fastapi -f
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal (cron)
sudo certbot renew --dry-run
```

## Health Check Endpoint

Add to your FastAPI app:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy"}
```

## Production Checklist

- [ ] Set strong SECRET_KEY in environment variables
- [ ] Use environment variables for all sensitive config
- [ ] Enable HTTPS/TLS
- [ ] Set up proper logging and monitoring
- [ ] Configure CORS appropriately
- [ ] Implement rate limiting
- [ ] Set up database backups
- [ ] Use connection pooling for databases
- [ ] Configure proper worker count (CPU cores * 2 + 1)
- [ ] Set up health checks
- [ ] Implement graceful shutdown
- [ ] Use reverse proxy (Nginx/Traefik)
- [ ] Set up CI/CD pipeline
- [ ] Configure auto-scaling
- [ ] Implement proper error handling
- [ ] Set up alerts and monitoring (Prometheus, Grafana, Sentry)
