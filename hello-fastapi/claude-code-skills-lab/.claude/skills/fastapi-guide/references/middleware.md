# FastAPI Middleware Reference

Complete guide to implementing middleware in FastAPI applications for cross-cutting concerns like CORS, timing, logging, and custom request/response processing.

## Table of Contents
- [What is Middleware?](#what-is-middleware)
- [CORS Middleware](#cors-middleware)
- [Custom HTTP Middleware](#custom-http-middleware)
- [Request Timing Middleware](#request-timing-middleware)
- [Common Middleware Patterns](#common-middleware-patterns)
- [Third-Party Middleware](#third-party-middleware)
- [Best Practices](#best-practices)

## What is Middleware?

Middleware is software that sits between the client and your route handlers, processing requests before they reach your endpoints and responses before they're sent to clients.

**Execution order:**
1. Request comes in
2. Middleware processes request (top to bottom)
3. Route handler executes
4. Middleware processes response (bottom to top)
5. Response sent to client

## CORS Middleware

Cross-Origin Resource Sharing (CORS) allows your API to accept requests from web applications hosted on different domains.

### Basic CORS Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "CORS enabled"}
```

### Production CORS Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Comma-separated list of allowed origins
    allowed_origins: str = "http://localhost:3000,https://myapp.com"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI()

# Production-ready CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

### CORS Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `allow_origins` | List of allowed origins | `["https://example.com"]` |
| `allow_origin_regex` | Regex pattern for origins | `r"https://.*\.example\.com"` |
| `allow_methods` | Allowed HTTP methods | `["GET", "POST"]` |
| `allow_headers` | Allowed request headers | `["*"]` or `["Authorization", "Content-Type"]` |
| `allow_credentials` | Allow cookies/auth | `True` or `False` |
| `expose_headers` | Headers visible to browser | `["X-Request-ID"]` |
| `max_age` | Cache preflight (seconds) | `3600` |

### Environment-Based CORS

**.env:**
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Production
# ALLOWED_ORIGINS=https://myapp.com,https://www.myapp.com
```

**config.py:**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    allowed_origins: str

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()
```

**main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Custom HTTP Middleware

### Using @app.middleware Decorator

The `@app.middleware("http")` decorator creates custom middleware that processes all HTTP requests.

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Add custom header to response
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response

@app.get("/")
async def root():
    return {"message": "Check X-Process-Time header"}
```

**How it works:**
1. `request: Request` - The incoming request object
2. `call_next` - Function that passes request to the next middleware or route handler
3. `response = await call_next(request)` - Get the response
4. Modify response as needed
5. Return the response

### Middleware Template

```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # --- Before request processing ---
    # Access request.method, request.url, request.headers, etc.

    # Process the request
    response = await call_next(request)

    # --- After request processing ---
    # Modify response.headers, response.status_code, etc.

    return response
```

## Request Timing Middleware

### Basic Timing Middleware

```python
from fastapi import FastAPI, Request
import time
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.4f}s "
        f"with status {response.status_code}"
    )

    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    return response
```

### Advanced Timing with Metrics

```python
from fastapi import FastAPI, Request
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

@app.middleware("http")
async def detailed_timing_middleware(request: Request, call_next):
    request_id = str(datetime.now().timestamp())

    # Log request start
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - Started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        }
    )

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Log successful response
        logger.info(
            f"[{request_id}] Completed in {process_time:.4f}s - "
            f"Status: {response.status_code}",
            extra={
                "request_id": request_id,
                "duration": process_time,
                "status_code": response.status_code,
            }
        )

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        return response

    except Exception as e:
        process_time = time.perf_counter() - start_time

        # Log error
        logger.error(
            f"[{request_id}] Failed after {process_time:.4f}s - Error: {str(e)}",
            extra={
                "request_id": request_id,
                "duration": process_time,
                "error": str(e),
            },
            exc_info=True
        )
        raise
```

## Common Middleware Patterns

### 1. Request ID Middleware

Add unique ID to each request for tracing.

```python
from fastapi import FastAPI, Request
import uuid

app = FastAPI()

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())

    # Add to request state for access in route handlers
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response

# Access in route handlers
@app.get("/")
async def root(request: Request):
    return {"request_id": request.state.request_id}
```

### 2. Security Headers Middleware

Add security headers to all responses.

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response
```

### 3. Request Logging Middleware

Log all incoming requests.

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )

    response = await call_next(request)
    return response
```

### 4. Rate Limiting Middleware

Basic rate limiting by IP address.

```python
from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import time

app = FastAPI()

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)
RATE_LIMIT = 100  # requests
RATE_PERIOD = 60  # seconds

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not request.client:
        return await call_next(request)

    client_ip = request.client.host
    now = time.time()

    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if now - req_time < RATE_PERIOD
    ]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    # Record this request
    request_counts[client_ip].append(now)

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(
        RATE_LIMIT - len(request_counts[client_ip])
    )

    return response
```

### 5. Error Handling Middleware

Catch and format errors consistently.

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(
            f"Unhandled error: {str(e)}",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "path": request.url.path,
            }
        )
```

### 6. Authentication Middleware

Check authentication on all requests (except public endpoints).

```python
from fastapi import Request, HTTPException

PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json"}

@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    # Skip auth for public paths
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    # Check for auth token
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.replace("Bearer ", "")

    # Validate token (simplified - use proper JWT validation)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Add user info to request state
    request.state.user = {"id": 1, "username": "user"}

    return await call_next(request)
```

## Third-Party Middleware

### Trusted Host Middleware

Prevent HTTP Host Header attacks.

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com", "localhost"]
)
```

### GZip Middleware

Compress responses for clients that support it.

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
```

### HTTPS Redirect Middleware

Force HTTPS in production.

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Only in production
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### Starlette Session Middleware

Add session support.

```bash
uv add itsdangerous
```

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # Use environment variable
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,  # 14 days
    same_site="lax",
    https_only=True  # In production
)

@app.get("/")
async def root(request: Request):
    # Access session
    request.session["user_id"] = 123
    return {"session": dict(request.session)}
```

## Best Practices

### 1. Middleware Order Matters

Add middleware in the correct order (top to bottom in code = outer to inner in execution):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# 1. Trusted Host (validate host first)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

# 2. CORS (handle CORS before other processing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. GZip (compress responses last)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Custom middleware
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    # Your custom logic
    response = await call_next(request)
    return response
```

**Execution flow:**
- Request: TrustedHost → CORS → GZip → Custom → Route Handler
- Response: Route Handler → Custom → GZip → CORS → TrustedHost

### 2. Use Request State for Data Sharing

```python
@app.middleware("http")
async def add_user_middleware(request: Request, call_next):
    # Add data to request state
    request.state.user_id = 123
    request.state.start_time = time.time()

    response = await call_next(request)
    return response

@app.get("/")
async def root(request: Request):
    # Access in route handler
    return {"user_id": request.state.user_id}
```

### 3. Environment-Specific Middleware

```python
from fastapi import FastAPI
from config import settings

app = FastAPI()

# Always add CORS
app.add_middleware(CORSMiddleware, **settings.cors_config)

# Production-only middleware
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Development-only middleware
if settings.environment == "development":
    @app.middleware("http")
    async def debug_middleware(request: Request, call_next):
        print(f"DEBUG: {request.method} {request.url}")
        response = await call_next(request)
        return response
```

### 4. Async All The Way

Always use `async def` for middleware to avoid blocking:

```python
# Good - Async
@app.middleware("http")
async def good_middleware(request: Request, call_next):
    response = await call_next(request)
    return response

# Bad - Sync (blocks the event loop)
@app.middleware("http")
def bad_middleware(request: Request, call_next):
    response = call_next(request)  # Missing await
    return response
```

### 5. Handle Exceptions Properly

```python
@app.middleware("http")
async def safe_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"Middleware error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

### 6. Performance Considerations

```python
import time

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    # Keep middleware logic minimal
    # Avoid heavy computations or blocking I/O

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    # Log slow requests
    if duration > 1.0:  # 1 second
        logger.warning(f"Slow request: {request.url.path} took {duration:.2f}s")

    return response
```

## Complete Example

Putting it all together in a production-ready setup:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic_settings import BaseSettings
import time
import logging
import uuid

# Configuration
class Settings(BaseSettings):
    environment: str = "development"
    allowed_origins: str = "http://localhost:3000"
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    class Config:
        env_file = ".env"

settings = Settings()
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="My API")

# 1. Trusted hosts
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response

# 5. Timing and logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    logger.info(
        f"[{request.state.request_id}] {request.method} {request.url.path} - Started"
    )

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        logger.info(
            f"[{request.state.request_id}] Completed in {process_time:.4f}s - "
            f"Status: {response.status_code}"
        )

        return response

    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.error(
            f"[{request.state.request_id}] Failed after {process_time:.4f}s",
            exc_info=True
        )
        raise

# 6. Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response

# Routes
@app.get("/")
async def root(request: Request):
    return {
        "message": "Hello World",
        "request_id": request.state.request_id
    }
```

## Summary

**Key Takeaways:**
1. Use `CORSMiddleware` for cross-origin requests
2. Use `@app.middleware("http")` for custom middleware
3. Middleware executes in order: outer → inner for requests, inner → outer for responses
4. Always use `async def` for middleware
5. Use `request.state` to share data between middleware and route handlers
6. Add security headers, request IDs, and timing for production apps
7. Keep middleware logic minimal for best performance

**Next Steps:**
- Add CORS to your API: See [CORS Middleware](#cors-middleware)
- Implement request timing: See [Request Timing Middleware](#request-timing-middleware)
- Add security headers: See [Security Headers Middleware](#common-middleware-patterns)
- Review deployment best practices: See [deployment.md](deployment.md)
