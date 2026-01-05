# Authentication & Authorization

Complete guide for implementing authentication in FastAPI with OAuth2, JWT, and session-based approaches.

## Table of Contents

- JWT Token Authentication (OAuth2 + Bearer)
- Password Hashing with bcrypt
- OAuth2 Password Flow
- Session-Based Authentication
- API Key Authentication
- Role-Based Access Control (RBAC)

## JWT Token Authentication

### Dependencies

```bash
uv add "python-jose[cryptography]" passlib bcrypt python-multipart
```

### Configuration (`auth/config.py`)

```python
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"


auth_settings = AuthSettings()
```

### Password Hashing (`auth/security.py`)

```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from .config import auth_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=auth_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[auth_settings.ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None
```

### Auth Schemas (`auth/schemas.py`)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
```

### Dependencies (`auth/dependencies.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db
import models
from .security import verify_token
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    result = await db.execute(select(models.User).filter(models.User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Ensure user is active."""
    if not getattr(current_user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_admin(
    current_user: models.User = Depends(get_current_active_user)
) -> models.User:
    """Require admin role."""
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### Auth Router (`auth/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
import models
from .schemas import Token, UserRegister, UserLogin
from .security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(
        select(models.User).filter(
            (models.User.username == user_data.username) | (models.User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )

    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    # Create tokens
    access_token = create_access_token(data={"sub": new_user.username, "user_id": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.username, "user_id": new_user.id})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with username and password."""
    result = await db.execute(
        select(models.User).filter(models.User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": user.id})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    payload = verify_token(refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")
    user_id = payload.get("user_id")

    access_token = create_access_token(data={"sub": username, "user_id": user_id})
    new_refresh_token = create_refresh_token(data={"sub": username, "user_id": user_id})

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me")
async def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
```

### Protected Routes Example

```python
from fastapi import APIRouter, Depends
from auth.dependencies import get_current_active_user, require_admin
import models

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/user")
async def user_route(current_user: models.User = Depends(get_current_active_user)):
    """Route accessible to any authenticated user."""
    return {"message": f"Hello {current_user.username}"}


@router.get("/admin")
async def admin_route(current_user: models.User = Depends(require_admin)):
    """Route accessible only to admins."""
    return {"message": "Admin access granted"}
```

## API Key Authentication

### Configuration

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Store API keys (use database in production)
VALID_API_KEYS = {
    "sk_test_abc123": {"name": "Test Key", "permissions": ["read", "write"]},
    "sk_prod_xyz789": {"name": "Production Key", "permissions": ["read"]},
}


async def get_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Validate API key."""
    if api_key is None or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return VALID_API_KEYS[api_key]
```

### Using API Key

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/data")
async def get_data(api_key_info: dict = Depends(get_api_key)):
    """Endpoint protected by API key."""
    return {
        "message": "Access granted",
        "key_name": api_key_info["name"],
        "permissions": api_key_info["permissions"]
    }
```

## Role-Based Access Control (RBAC)

### User Model with Roles

```python
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Many-to-many relationship
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
```

### RBAC Dependencies

```python
from fastapi import Depends, HTTPException, status
from typing import List
from auth.dependencies import get_current_active_user
import models


def require_roles(required_roles: List[str]):
    """Create a dependency that requires specific roles."""
    async def role_checker(current_user: models.User = Depends(get_current_active_user)):
        user_roles = [role.name for role in current_user.roles]

        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return role_checker


def require_permissions(required_permissions: List[str]):
    """Create a dependency that requires specific permissions."""
    async def permission_checker(current_user: models.User = Depends(get_current_active_user)):
        user_permissions = []
        for role in current_user.roles:
            user_permissions.extend([perm.name for perm in role.permissions])

        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return permission_checker
```

### Using RBAC

```python
from fastapi import APIRouter, Depends
from auth.rbac import require_roles, require_permissions

router = APIRouter()


@router.get("/admin/dashboard")
async def admin_dashboard(user = Depends(require_roles(["admin", "superadmin"]))):
    """Only accessible to admins and superadmins."""
    return {"message": "Admin dashboard"}


@router.post("/posts")
async def create_post(user = Depends(require_permissions(["create_post"]))):
    """Only accessible to users with create_post permission."""
    return {"message": "Post created"}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user = Depends(require_permissions(["delete_post"]))
):
    """Only accessible to users with delete_post permission."""
    return {"message": f"Post {post_id} deleted"}
```

## Environment Variables (.env)

```bash
# Authentication
SECRET_KEY=your-very-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```
