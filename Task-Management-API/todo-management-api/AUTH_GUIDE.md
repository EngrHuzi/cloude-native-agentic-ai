# Authentication Guide

This Todo Management API now includes secure user authentication using **Argon2 password hashing** and **JWT tokens**.

## 🔐 Security Features

- **Argon2id password hashing** - The gold standard for password security
- **JWT-based authentication** - Secure token-based access
- **Refresh tokens** - Long-lived tokens for obtaining new access tokens
- **User isolation** - Each user can only access their own todos

## 📋 Quick Start

### 1. Register a New User

**Endpoint:** `POST /auth/register`

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login

**Endpoint:** `POST /auth/login`

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securePassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User Info

**Endpoint:** `GET /auth/me`

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-12T10:30:00"
}
```

### 4. Refresh Access Token

**Endpoint:** `POST /auth/refresh`

```bash
curl -X POST "http://localhost:8000/auth/refresh?refresh_token=YOUR_REFRESH_TOKEN"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 📝 Using Authenticated Todo Endpoints

All todo endpoints now require authentication. Include the access token in the Authorization header:

### Create a Todo

```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the authentication implementation",
    "priority": "high",
    "status": "todo"
  }'
```

### Get All Todos (for current user)

```bash
curl -X GET "http://localhost:8000/todos/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Update a Todo

```bash
curl -X PATCH "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### Delete a Todo

```bash
curl -X DELETE "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔑 Token Management

### Access Tokens
- **Lifetime:** 30 minutes (configurable)
- **Purpose:** Authenticate API requests
- **Storage:** Store securely (e.g., memory, secure storage)

### Refresh Tokens
- **Lifetime:** 7 days (configurable)
- **Purpose:** Obtain new access tokens without re-login
- **Storage:** Store securely (e.g., httpOnly cookies, secure storage)

### Token Expiration Flow

1. Use **access_token** for API requests
2. When access_token expires (401 error), use **refresh_token** to get a new access_token
3. When refresh_token expires, user must login again

## 🛡️ Security Best Practices

### Password Requirements
- Minimum 8 characters
- Use a mix of letters, numbers, and special characters
- Passwords are hashed with Argon2id before storage
- **Never** stored in plain text

### Secret Key Management
- Generate with: `openssl rand -hex 32`
- Store in `.env` file (never commit to git)
- Rotate periodically in production
- Use different keys for development and production

### Environment Variables

Add to your `.env` file:

```bash
# Authentication Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🧪 Testing with Swagger UI

1. Start the server: `fastapi dev main.py`
2. Open: http://localhost:8000/docs
3. Click "Authorize" button (🔓 icon)
4. Register/login to get a token
5. Enter token in format: `Bearer YOUR_TOKEN`
6. Click "Authorize"
7. Now you can test all protected endpoints

## 📊 Database Changes

### New Tables
- **users**: Stores user accounts with hashed passwords

### Modified Tables
- **todos**: Added `user_id` foreign key to associate todos with users

### Migration Note
If you have existing data, you'll need to:
1. Create a default user
2. Assign existing todos to that user
3. Or drop and recreate the database

## 🔍 Common Issues

### 401 Unauthorized
- Token expired - use refresh token to get a new access token
- Invalid token - login again
- Missing Authorization header - include `Authorization: Bearer TOKEN`

### 404 Todo Not Found
- Todo belongs to another user
- Todo ID doesn't exist
- Check you're querying the right endpoint

### 400 Bad Request
- Username/email already exists
- Invalid input data
- Check request body format

## 🚀 Next Steps

Consider adding:
- Email verification
- Password reset functionality
- OAuth2 providers (Google, GitHub)
- Role-based access control (RBAC)
- Rate limiting
- Account lockout after failed attempts

## 📚 API Reference

Full API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
