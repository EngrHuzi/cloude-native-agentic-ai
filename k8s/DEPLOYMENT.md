# Kubernetes Deployment Guide

This guide explains how to deploy the Todo Management API to a local Kubernetes cluster.

## Prerequisites

- Kubernetes cluster running locally (Minikube, Kind, Docker Desktop K8s, or k3s)
- `kubectl` CLI installed
- For Kind/Minikube: `kubectl` configured to talk to your cluster

## Quick Start

### 1. Verify Cluster Connection

```bash
# Check cluster info
kubectl cluster-info

# List nodes
kubectl get nodes

# Check current context
kubectl config current-context
```

### 2. Create Namespace

```bash
# Create namespace for the application
kubectl create namespace todo-api
```

### 3. Deploy Application

**Option A: Deploy with Kustomize (Recommended)**

```bash
# Apply all manifests using Kustomize
kubectl apply -k k8s/

# Wait for deployments to be ready
kubectl wait --for=condition=available --timeout=120s deployment/todo-api -n todo-api
kubectl wait --for=condition=ready --timeout=60s pod -l app=todo-api -n todo-api
```

**Option B: Deploy Individual Manifests**

```bash
# Apply secrets first
kubectl apply -f k8s/secrets.yaml -n todo-api

# Apply PostgreSQL deployment
kubectl apply -f k8s/postgres-deployment.yaml -n todo-api

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready --timeout=60s pod -l app=postgres -n todo-api

# Apply API deployment
kubectl apply -f k8s/deployment.yaml -n todo-api

# Apply service
kubectl apply -f k8s/service.yaml -n todo-api
```

### 4. Verify Deployment

```bash
# Check all resources in namespace
kubectl get all -n todo-api

# Check deployment status
kubectl get deployment todo-api -n todo-api

# Check pods
kubectl get pods -n todo-api

# Describe pod for details
kubectl describe pod -l app=todo-api -n todo-api

# Check service
kubectl get service todo-api -n todo-api

# Check HPA
kubectl get hpa -n todo-api
```

### 5. Access the Application

**For Minikube:**

```bash
# Get the URL
minikube service todo-api -n todo-api --url

# Or open in browser
minikube service todo-api -n todo-api
```

**For Docker Desktop Kubernetes:**

```bash
# Get node port
kubectl get service todo-api -n todo-api

# Access via: http://localhost:30080
# Or use the NodeIP with NodePort
```

**For Kind:**

```bash
# Get node port
NODE_PORT=$(kubectl get service todo-api -n todo-api -o jsonpath='{.spec.ports[0].nodePort}')

# Port forward to localhost
kubectl port-forward -n todo-api service/todo-api 8000:8000

# Access via: http://localhost:8000
```

**Port Forwarding (Universal):**

```bash
# Forward local port 8000 to service port 8000
kubectl port-forward -n todo-api service/todo-api 8000:8000

# Access the API at: http://localhost:8000
# Or: http://localhost:8000/docs for Swagger UI
```

### 6. Test the Deployment

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/

# With port forwarding
kubectl port-forward -n todo-api service/todo-api 8000:8000 &
curl http://localhost:8000/health
```

## Scaling

### Manual Scaling

```bash
# Scale to 4 replicas
kubectl scale deployment todo-api --replicas=4 -n todo-api

# Verify
kubectl get pods -n todo-api
```

### Auto Scaling (HPA)

The deployment includes a HorizontalPodAutoscaler that:
- Maintains **2-10 replicas**
- Scales based on **CPU (70%)** and **Memory (80%)** usage

```bash
# Check HPA status
kubectl get hpa -n todo-api
kubectl describe hpa todo-api-hpa -n todo-api

# Manually trigger load test for auto-scaling
kubectl run -it --rm load-test --image=busybox --restart=Never -- sh -c "while true; do wget -q -O- http://todo-api:8000/health; done"
```

## Viewing Logs

```bash
# Logs from all pods
kubectl logs -l app=todo-api -n todo-api --tail=50 -f

# Logs from specific pod
kubectl logs <pod-name> -n todo-api -f

# Logs from PostgreSQL
kubectl logs -l app=postgres -n todo-api --tail=50 -f
```

## Updating Secrets

**IMPORTANT: Update the secrets.yaml before deploying!**

```bash
# Generate a secure secret key
openssl rand -hex 32

# Edit secrets
kubectl edit secret todo-api-secrets -n todo-api

# Or delete and recreate
kubectl delete secret todo-api-secrets -n todo-api
kubectl apply -f k8s/secrets.yaml -n todo-api

# Restart pods to pick up new secrets
kubectl rollout restart deployment todo-api -n todo-api
```

## Rolling Updates

```bash
# Trigger a rollout restart
kubectl rollout restart deployment todo-api -n todo-api

# Check rollout status
kubectl rollout status deployment/todo-api -n todo-api

# View rollout history
kubectl rollout history deployment/todo-api -n todo-api

# Rollback to previous version
kubectl rollout undo deployment/todo-api -n todo-api

# Rollback to specific revision
kubectl rollout undo deployment/todo-api --to-revision=2 -n todo-api
```

## Troubleshooting

### Pod Not Starting

```bash
# Describe pod to see events
kubectl describe pod <pod-name> -n todo-api

# Check logs
kubectl logs <pod-name> -n todo-api

# Check pod events
kubectl get events -n todo-api --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
kubectl get pods -l app=postgres -n todo-api

# Test database connection
kubectl exec -it <postgres-pod-name> -n todo-api -- psql -U postgres -d todo_db -c "SELECT 1"

# Check database URL in secret
kubectl get secret todo-api-secrets -n todo-api -o jsonpath='{.data.database-url}' | base64 -d
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints todo-api -n todo-api

# Check if pods have IP addresses
kubectl get pods -n todo-api -o wide

# Test service from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -qO- http://todo-api:8000/health
```

## Cleanup

```bash
# Delete all resources (using Kustomize)
kubectl delete -k k8s/

# Or delete namespace (deletes everything in it)
kubectl delete namespace todo-api

# Delete individual resources
kubectl delete deployment todo-api -n todo-api
kubectl delete service todo-api -n todo-api
kubectl delete hpa todo-api-hpa -n todo-api
kubectl delete deployment postgres -n todo-api
kubectl delete service postgres-service -n todo-api
kubectl delete pvc postgres-pvc -n todo-api
kubectl delete secret todo-api-secrets -n todo-api
```

## Configuration Reference

### Deployment Settings

| Setting | Value | Description |
|---------|-------|-------------|
| Replicas | 2 | Initial pod count |
| Min Replicas (HPA) | 2 | Minimum auto-scaled pods |
| Max Replicas (HPA) | 10 | Maximum auto-scaled pods |
| CPU Target | 70% | Scale up threshold |
| Memory Target | 80% | Scale up threshold |
| Container Port | 8000 | Application port |

### Service Settings

| Setting | Value | Description |
|---------|-------|-------------|
| Type | NodePort | Exposes service on node port |
| Port | 8000 | Service port |
| Target Port | 8000 | Container port |
| NodePort | 30080 | Node port for external access |

### Resource Limits

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 512Mi |

## Production Considerations

Before deploying to production:

1. **Update Secrets**: Generate secure random keys and passwords
2. **Configure Ingress**: Use an Ingress controller for external access
3. **TLS/SSL**: Enable HTTPS with certificates
4. **Persistent Storage**: Use persistent volumes for PostgreSQL
5. **Monitoring**: Add Prometheus/Grafana for metrics
6. **Logging**: Centralized logging (ELK, Loki)
7. **Image Registry**: Use private registry for production images
8. **Network Policies**: Restrict pod-to-pod communication
9. **RBAC**: Configure proper role-based access control
10. **Backup**: Implement database backup strategy

## Next Steps

- Set up Ingress controller for routing
- Configure TLS certificates
- Add monitoring and alerting
- Implement CI/CD pipeline
- Set up staging environment
