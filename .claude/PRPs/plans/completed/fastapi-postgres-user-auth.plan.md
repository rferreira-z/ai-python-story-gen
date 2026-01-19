# Feature: Production-Ready FastAPI with PostgreSQL, pgvector, User Module & Authentication

## Summary

Build a secure, performant, production-ready FastAPI backend with PostgreSQL (SQL + pgvector) support, Docker containerization, a complete user module (CRUD APIs, services, repositories), and email/password authentication using JWT tokens. The architecture follows a layered service pattern with async SQLAlchemy 2.0, proper separation of concerns, and industry-standard security practices.

## User Story

As a developer
I want a production-ready FastAPI backend with user management and authentication
So that I can build secure applications with PostgreSQL and vector search capabilities

## Problem Statement

Starting a new Python API project requires significant boilerplate: setting up secure authentication, database connections with async support, proper project structure, Docker configuration, and vector search capabilities. This foundation must be secure, performant, and follow best practices to avoid technical debt.

## Solution Statement

Implement a layered FastAPI application with:
- **Async SQLAlchemy 2.0** with asyncpg driver for PostgreSQL
- **pgvector** extension for vector similarity search
- **JWT-based authentication** with bcrypt password hashing (via pwdlib, not deprecated passlib)
- **Repository pattern** for database operations
- **Service layer** for business logic
- **Pydantic v2** for validation and settings
- **Alembic** for database migrations
- **Docker Compose** for development and production environments

## Metadata

| Field            | Value                                                              |
| ---------------- | ------------------------------------------------------------------ |
| Type             | NEW_CAPABILITY                                                     |
| Complexity       | HIGH                                                               |
| Systems Affected | FastAPI, PostgreSQL, pgvector, Docker, Authentication, User Module |
| Dependencies     | fastapi, sqlalchemy[asyncio], asyncpg, pgvector, pydantic-settings, python-jose[cryptography], pwdlib[argon2,bcrypt], alembic, uvicorn |
| Estimated Tasks  | 25                                                                 |

---

## UX Design

### Before State
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              BEFORE STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────┐                                                             ║
║   │   Empty     │                                                             ║
║   │   Project   │                                                             ║
║   │  Directory  │                                                             ║
║   └─────────────┘                                                             ║
║                                                                               ║
║   USER_FLOW: No API exists                                                    ║
║   PAIN_POINT: Need to build everything from scratch                           ║
║   DATA_FLOW: None                                                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### After State
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                               AFTER STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               ║
║   │   Client     │─────►│   FastAPI    │─────►│  PostgreSQL  │               ║
║   │  (Browser/   │      │   + Auth     │      │  + pgvector  │               ║
║   │   Mobile)    │◄─────│   + Users    │◄─────│              │               ║
║   └──────────────┘      └──────────────┘      └──────────────┘               ║
║          │                     │                                              ║
║          │                     ▼                                              ║
║          │              ┌──────────────┐                                      ║
║          │              │    Docker    │                                      ║
║          │              │   Compose    │                                      ║
║          │              └──────────────┘                                      ║
║          │                                                                    ║
║          ▼                                                                    ║
║   ┌────────────────────────────────────────────────────────────────┐         ║
║   │                        API Endpoints                            │         ║
║   ├─────────────────────┬──────────────────────────────────────────┤         ║
║   │ POST /auth/register │ Create new user account                   │         ║
║   │ POST /auth/login    │ Get JWT access + refresh tokens           │         ║
║   │ POST /auth/refresh  │ Refresh access token                      │         ║
║   │ GET  /users/me      │ Get current user profile                  │         ║
║   │ PUT  /users/me      │ Update current user                       │         ║
║   │ GET  /users/{id}    │ Get user by ID (admin)                    │         ║
║   │ GET  /users         │ List all users (admin)                    │         ║
║   │ PUT  /users/{id}    │ Update user (admin)                       │         ║
║   │ DELETE /users/{id}  │ Delete user (admin)                       │         ║
║   │ GET  /health        │ Health check endpoint                     │         ║
║   └─────────────────────┴──────────────────────────────────────────┘         ║
║                                                                               ║
║   USER_FLOW:                                                                  ║
║   1. Register → Login → Get JWT → Access protected endpoints                  ║
║   2. Token expires → Use refresh token → Get new access token                 ║
║                                                                               ║
║   VALUE_ADD:                                                                  ║
║   - Secure authentication out of the box                                      ║
║   - Production-ready Docker setup                                             ║
║   - Vector search capability for AI/ML features                               ║
║   - Clean, maintainable architecture                                          ║
║                                                                               ║
║   DATA_FLOW:                                                                  ║
║   Request → Router → Service → Repository → Database → Response               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Interaction Changes

| Location              | Before   | After                          | User Impact                      |
| --------------------- | -------- | ------------------------------ | -------------------------------- |
| `/auth/register`      | N/A      | User registration              | Can create accounts              |
| `/auth/login`         | N/A      | JWT token issuance             | Secure authentication            |
| `/users/*`            | N/A      | Full CRUD operations           | Manage user data                 |
| `/health`             | N/A      | Liveness/readiness checks      | Load balancer integration        |
| `/docs`               | N/A      | OpenAPI documentation          | API exploration                  |

---

## Mandatory Reading

**CRITICAL: This is a greenfield project - no existing codebase patterns to mirror**

| Priority | Source                                           | Why Read This                               |
| -------- | ------------------------------------------------ | ------------------------------------------- |
| P0       | [FastAPI Official Docs](https://fastapi.tiangolo.com/tutorial/bigger-applications/) | Project structure patterns                  |
| P0       | [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) | Async session management, gotchas           |
| P1       | [FastAPI JWT Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) | Authentication implementation               |
| P1       | [pgvector Python](https://github.com/pgvector/pgvector-python) | Vector type integration with SQLAlchemy     |
| P2       | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Environment configuration                   |

**Key Gotchas from Research:**

1. **passlib is deprecated** - Use `pwdlib` instead for password hashing
2. **bcrypt 72-byte limit** - Consider Argon2 for longer passwords
3. **AsyncSession expire_on_commit** - Disable to prevent issues with detached objects
4. **SQLAlchemy session per task** - Never share AsyncSession across tasks
5. **Docker hostname** - Use service name (not localhost) for DB connection in Docker

---

## Patterns to Establish

**PROJECT_STRUCTURE:**
```
app/
├── __init__.py
├── main.py                 # FastAPI app creation, middleware, routers
├── core/
│   ├── __init__.py
│   ├── config.py           # Pydantic settings
│   ├── security.py         # JWT, password hashing
│   └── database.py         # Async engine, session factory
├── models/
│   ├── __init__.py
│   └── user.py             # SQLAlchemy ORM models
├── schemas/
│   ├── __init__.py
│   ├── user.py             # Pydantic schemas for users
│   └── auth.py             # Pydantic schemas for auth
├── repositories/
│   ├── __init__.py
│   └── user.py             # Database operations
├── services/
│   ├── __init__.py
│   ├── user.py             # User business logic
│   └── auth.py             # Auth business logic
├── api/
│   ├── __init__.py
│   ├── deps.py             # Dependency injection
│   └── v1/
│       ├── __init__.py
│       ├── router.py       # API v1 router aggregator
│       ├── users.py        # User endpoints
│       └── auth.py         # Auth endpoints
└── migrations/             # Alembic migrations
    ├── env.py
    ├── script.py.mako
    └── versions/
```

**CONFIG_PATTERN:**
```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "FastAPI App"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str
    database_echo: bool = False

    # Auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

settings = Settings()
```

**DATABASE_PATTERN:**
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: Prevents detached object issues
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**REPOSITORY_PATTERN:**
```python
# app/repositories/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
```

**SERVICE_PATTERN:**
```python
# app/services/user.py
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from app.core.security import get_password_hash

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_in: UserCreate) -> User:
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
        )
        return await self.repository.create(user)
```

**SECURITY_PATTERN:**
```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Use Argon2 (OWASP 2025 recommendation)
password_hash = PasswordHash((Argon2Hasher(),))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
```

**DEPENDENCY_PATTERN:**
```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user
```

**ERROR_HANDLING_PATTERN:**
```python
# app/core/exceptions.py
from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class ConflictError(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
```

**TEST_PATTERN:**
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
```

---

## Files to Create

| File                              | Action | Justification                                  |
| --------------------------------- | ------ | ---------------------------------------------- |
| `pyproject.toml`                  | CREATE | Project metadata and dependencies              |
| `.env.example`                    | CREATE | Environment variable template                  |
| `.gitignore`                      | CREATE | Git ignore patterns                            |
| `docker-compose.yml`              | CREATE | Development environment                        |
| `docker-compose.prod.yml`         | CREATE | Production environment                         |
| `Dockerfile`                      | CREATE | Application container                          |
| `app/__init__.py`                 | CREATE | Package init                                   |
| `app/main.py`                     | CREATE | FastAPI application entry point                |
| `app/core/__init__.py`            | CREATE | Core package init                              |
| `app/core/config.py`              | CREATE | Pydantic settings configuration                |
| `app/core/database.py`            | CREATE | Async SQLAlchemy setup with pgvector           |
| `app/core/security.py`            | CREATE | JWT and password hashing utilities             |
| `app/core/exceptions.py`          | CREATE | Custom HTTP exceptions                         |
| `app/models/__init__.py`          | CREATE | Models package init                            |
| `app/models/user.py`              | CREATE | User SQLAlchemy model                          |
| `app/schemas/__init__.py`         | CREATE | Schemas package init                           |
| `app/schemas/user.py`             | CREATE | User Pydantic schemas                          |
| `app/schemas/auth.py`             | CREATE | Auth Pydantic schemas (Token, Login, etc.)     |
| `app/repositories/__init__.py`    | CREATE | Repositories package init                      |
| `app/repositories/user.py`        | CREATE | User database operations                       |
| `app/services/__init__.py`        | CREATE | Services package init                          |
| `app/services/user.py`            | CREATE | User business logic                            |
| `app/services/auth.py`            | CREATE | Authentication business logic                  |
| `app/api/__init__.py`             | CREATE | API package init                               |
| `app/api/deps.py`                 | CREATE | Dependency injection                           |
| `app/api/v1/__init__.py`          | CREATE | API v1 package init                            |
| `app/api/v1/router.py`            | CREATE | API v1 router aggregator                       |
| `app/api/v1/users.py`             | CREATE | User CRUD endpoints                            |
| `app/api/v1/auth.py`              | CREATE | Authentication endpoints                       |
| `app/api/v1/health.py`            | CREATE | Health check endpoint                          |
| `alembic.ini`                     | CREATE | Alembic configuration                          |
| `app/migrations/env.py`           | CREATE | Alembic async migration environment            |
| `app/migrations/script.py.mako`   | CREATE | Alembic migration template                     |
| `tests/__init__.py`               | CREATE | Tests package init                             |
| `tests/conftest.py`               | CREATE | Pytest fixtures                                |
| `tests/test_auth.py`              | CREATE | Authentication endpoint tests                  |
| `tests/test_users.py`             | CREATE | User endpoint tests                            |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- **Email verification/password reset** - Requires email service integration, out of initial scope
- **OAuth2 social login** - Google/GitHub/etc. login requires external provider setup
- **Rate limiting** - Can be added later with slowapi or similar
- **Caching layer** - Redis integration not included in initial scope
- **Admin dashboard** - No frontend included
- **Role-based access control (RBAC)** - Basic is_admin flag only, no complex permissions
- **API key authentication** - JWT only for this version
- **WebSocket support** - Not needed for initial CRUD APIs
- **Background tasks/Celery** - Not included in initial scope
- **Kubernetes manifests** - Docker Compose only for this version

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

### Task 1: CREATE `pyproject.toml`

- **ACTION**: Create project configuration with all dependencies
- **IMPLEMENT**:
  ```toml
  [project]
  name = "fastapi-postgres-app"
  version = "0.1.0"
  description = "Production-ready FastAPI with PostgreSQL and pgvector"
  requires-python = ">=3.11"
  dependencies = [
      "fastapi>=0.115.0",
      "uvicorn[standard]>=0.32.0",
      "sqlalchemy[asyncio]>=2.0.36",
      "asyncpg>=0.30.0",
      "pgvector>=0.3.6",
      "pydantic>=2.10.0",
      "pydantic-settings>=2.6.0",
      "python-jose[cryptography]>=3.3.0",
      "pwdlib[argon2,bcrypt]>=0.2.0",
      "python-multipart>=0.0.17",
      "alembic>=1.14.0",
  ]

  [project.optional-dependencies]
  dev = [
      "pytest>=8.0.0",
      "pytest-asyncio>=0.24.0",
      "httpx>=0.28.0",
      "ruff>=0.8.0",
      "mypy>=1.13.0",
  ]
  ```
- **VALIDATE**: `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`

### Task 2: CREATE `.env.example`

- **ACTION**: Create environment variable template
- **IMPLEMENT**:
  ```
  # Application
  APP_NAME="FastAPI App"
  DEBUG=false
  API_V1_PREFIX="/api/v1"

  # Database (use asyncpg driver)
  DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"
  DATABASE_ECHO=false

  # Security (generate with: openssl rand -hex 32)
  SECRET_KEY="your-super-secret-key-change-in-production"
  ALGORITHM="HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS=7

  # Docker PostgreSQL
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres
  POSTGRES_DB=app_db
  ```
- **VALIDATE**: File exists and is parseable

### Task 3: CREATE `.gitignore`

- **ACTION**: Create Git ignore file for Python/FastAPI project
- **IMPLEMENT**: Standard Python .gitignore with `.env`, `__pycache__`, `.venv`, etc.
- **VALIDATE**: File exists

### Task 4: CREATE `Dockerfile`

- **ACTION**: Create multi-stage production Dockerfile
- **IMPLEMENT**:
  ```dockerfile
  FROM python:3.12-slim as builder

  WORKDIR /app

  RUN pip install --no-cache-dir uv

  COPY pyproject.toml .
  RUN uv pip install --system --no-cache -r pyproject.toml

  FROM python:3.12-slim

  WORKDIR /app

  COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
  COPY --from=builder /usr/local/bin /usr/local/bin

  COPY ./app ./app
  COPY ./alembic.ini .

  # Non-root user for security
  RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
  USER appuser

  EXPOSE 8000

  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- **VALIDATE**: `docker build -t test-build .` (after all files created)

### Task 5: CREATE `docker-compose.yml`

- **ACTION**: Create development Docker Compose configuration
- **IMPLEMENT**:
  ```yaml
  services:
    db:
      image: pgvector/pgvector:pg17
      environment:
        POSTGRES_USER: ${POSTGRES_USER:-postgres}
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
        POSTGRES_DB: ${POSTGRES_DB:-app_db}
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres"]
        interval: 5s
        timeout: 5s
        retries: 5

    app:
      build: .
      ports:
        - "8000:8000"
      environment:
        DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-app_db}
      depends_on:
        db:
          condition: service_healthy
      volumes:
        - ./app:/app/app  # Hot reload in dev

  volumes:
    postgres_data:
  ```
- **VALIDATE**: `docker compose config`

### Task 6: CREATE `app/__init__.py`

- **ACTION**: Create empty package init
- **IMPLEMENT**: Empty file or version string
- **VALIDATE**: `python -c "import app"`

### Task 7: CREATE `app/core/__init__.py`

- **ACTION**: Create core package init
- **IMPLEMENT**: Empty file
- **VALIDATE**: `python -c "import app.core"`

### Task 8: CREATE `app/core/config.py`

- **ACTION**: Create Pydantic settings configuration
- **IMPLEMENT**: Settings class with all environment variables (see PATTERNS section)
- **GOTCHA**: Use `SettingsConfigDict` not deprecated `class Config`
- **VALIDATE**: `python -c "from app.core.config import settings; print(settings.app_name)"`

### Task 9: CREATE `app/core/exceptions.py`

- **ACTION**: Create custom HTTP exception classes
- **IMPLEMENT**: NotFoundError, UnauthorizedError, ForbiddenError, ConflictError
- **VALIDATE**: `python -c "from app.core.exceptions import NotFoundError"`

### Task 10: CREATE `app/core/security.py`

- **ACTION**: Create JWT and password hashing utilities
- **IMPLEMENT**:
  - `verify_password()` using pwdlib with Argon2
  - `get_password_hash()` using pwdlib with Argon2
  - `create_access_token()` using python-jose
  - `create_refresh_token()` using python-jose
  - `decode_token()` for token validation
- **GOTCHA**: Use `pwdlib` not deprecated `passlib`; Use `datetime.now(timezone.utc)` not `datetime.utcnow()`
- **VALIDATE**: `python -c "from app.core.security import get_password_hash, verify_password; h = get_password_hash('test'); assert verify_password('test', h)"`

### Task 11: CREATE `app/core/database.py`

- **ACTION**: Create async SQLAlchemy setup with pgvector
- **IMPLEMENT**:
  - `Base` declarative base
  - `engine` async engine with asyncpg
  - `async_session_maker` with `expire_on_commit=False`
  - `get_db()` async generator dependency
- **GOTCHA**: Set `expire_on_commit=False` to prevent detached object issues
- **VALIDATE**: `python -c "from app.core.database import Base, async_session_maker"`

### Task 12: CREATE `app/models/__init__.py`

- **ACTION**: Create models package init, export all models
- **IMPLEMENT**: `from app.models.user import User`
- **VALIDATE**: `python -c "from app.models import User"`

### Task 13: CREATE `app/models/user.py`

- **ACTION**: Create User SQLAlchemy model
- **IMPLEMENT**:
  ```python
  from sqlalchemy import String, Boolean, DateTime, func
  from sqlalchemy.orm import Mapped, mapped_column
  from app.core.database import Base

  class User(Base):
      __tablename__ = "users"

      id: Mapped[int] = mapped_column(primary_key=True)
      email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
      hashed_password: Mapped[str] = mapped_column(String(255))
      full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
      is_active: Mapped[bool] = mapped_column(Boolean, default=True)
      is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
      created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
      updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
  ```
- **GOTCHA**: Use SQLAlchemy 2.0 `Mapped` type hints
- **VALIDATE**: `python -c "from app.models.user import User; print(User.__tablename__)"`

### Task 14: CREATE `app/schemas/__init__.py`

- **ACTION**: Create schemas package init
- **IMPLEMENT**: Export all schemas
- **VALIDATE**: `python -c "from app.schemas import UserCreate, UserResponse"`

### Task 15: CREATE `app/schemas/user.py`

- **ACTION**: Create User Pydantic schemas
- **IMPLEMENT**:
  - `UserBase` - shared fields
  - `UserCreate` - email, password, full_name
  - `UserUpdate` - optional fields for updates
  - `UserResponse` - public user data (no password)
  - `UserInDB` - internal with hashed_password
- **GOTCHA**: Use Pydantic v2 `model_config` not `class Config`
- **VALIDATE**: `python -c "from app.schemas.user import UserCreate; u = UserCreate(email='test@test.com', password='test123')"`

### Task 16: CREATE `app/schemas/auth.py`

- **ACTION**: Create Auth Pydantic schemas
- **IMPLEMENT**:
  - `Token` - access_token, refresh_token, token_type
  - `TokenPayload` - sub, exp
  - `LoginRequest` - username (email), password
- **VALIDATE**: `python -c "from app.schemas.auth import Token"`

### Task 17: CREATE `app/repositories/__init__.py`

- **ACTION**: Create repositories package init
- **IMPLEMENT**: Export UserRepository
- **VALIDATE**: `python -c "from app.repositories import UserRepository"`

### Task 18: CREATE `app/repositories/user.py`

- **ACTION**: Create User repository with database operations
- **IMPLEMENT**:
  - `get_by_id(user_id: int) -> User | None`
  - `get_by_email(email: str) -> User | None`
  - `get_all(skip: int, limit: int) -> list[User]`
  - `create(user: User) -> User`
  - `update(user: User, update_data: dict) -> User`
  - `delete(user: User) -> None`
- **GOTCHA**: Use `scalar_one_or_none()` not deprecated `first()`; Use `flush()` then `refresh()` after create
- **VALIDATE**: `python -c "from app.repositories.user import UserRepository"`

### Task 19: CREATE `app/services/__init__.py`

- **ACTION**: Create services package init
- **IMPLEMENT**: Export UserService, AuthService
- **VALIDATE**: `python -c "from app.services import UserService"`

### Task 20: CREATE `app/services/user.py`

- **ACTION**: Create User service with business logic
- **IMPLEMENT**:
  - `get_by_id(user_id: int) -> User` - raises NotFoundError
  - `get_by_email(email: str) -> User | None`
  - `get_all(skip: int, limit: int) -> list[User]`
  - `create_user(user_in: UserCreate) -> User` - raises ConflictError if email exists
  - `update_user(user_id: int, user_in: UserUpdate) -> User`
  - `delete_user(user_id: int) -> None`
- **VALIDATE**: `python -c "from app.services.user import UserService"`

### Task 21: CREATE `app/services/auth.py`

- **ACTION**: Create Auth service with authentication logic
- **IMPLEMENT**:
  - `authenticate_user(email: str, password: str) -> User | None`
  - `create_tokens(user: User) -> Token`
  - `refresh_access_token(refresh_token: str) -> Token`
- **VALIDATE**: `python -c "from app.services.auth import AuthService"`

### Task 22: CREATE `app/api/__init__.py`

- **ACTION**: Create API package init
- **IMPLEMENT**: Empty file
- **VALIDATE**: `python -c "from app import api"`

### Task 23: CREATE `app/api/deps.py`

- **ACTION**: Create dependency injection functions
- **IMPLEMENT**:
  - `get_db()` - re-export from database
  - `get_user_repository(db)` - returns UserRepository
  - `get_user_service(repo)` - returns UserService
  - `get_auth_service(repo)` - returns AuthService
  - `get_current_user(token)` - validates JWT, returns User
  - `get_current_active_user(user)` - checks is_active
  - `get_current_admin_user(user)` - checks is_admin
- **VALIDATE**: `python -c "from app.api.deps import get_current_user"`

### Task 24: CREATE `app/api/v1/__init__.py`

- **ACTION**: Create API v1 package init
- **IMPLEMENT**: Empty file
- **VALIDATE**: `python -c "from app.api import v1"`

### Task 25: CREATE `app/api/v1/health.py`

- **ACTION**: Create health check endpoint
- **IMPLEMENT**:
  ```python
  from fastapi import APIRouter, Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import text
  from app.core.database import get_db

  router = APIRouter(tags=["health"])

  @router.get("/health")
  async def health_check():
      return {"status": "healthy"}

  @router.get("/health/db")
  async def db_health_check(db: AsyncSession = Depends(get_db)):
      await db.execute(text("SELECT 1"))
      return {"status": "healthy", "database": "connected"}
  ```
- **VALIDATE**: After app runs, `curl localhost:8000/api/v1/health`

### Task 26: CREATE `app/api/v1/auth.py`

- **ACTION**: Create authentication endpoints
- **IMPLEMENT**:
  - `POST /auth/register` - create new user
  - `POST /auth/login` - OAuth2PasswordRequestForm, return tokens
  - `POST /auth/refresh` - refresh access token
- **GOTCHA**: OAuth2 spec requires `username` field (use email as username)
- **VALIDATE**: After app runs, test with curl or /docs

### Task 27: CREATE `app/api/v1/users.py`

- **ACTION**: Create User CRUD endpoints
- **IMPLEMENT**:
  - `GET /users/me` - get current user (authenticated)
  - `PUT /users/me` - update current user (authenticated)
  - `GET /users/{id}` - get user by ID (admin only)
  - `GET /users` - list all users (admin only)
  - `PUT /users/{id}` - update user (admin only)
  - `DELETE /users/{id}` - delete user (admin only)
- **VALIDATE**: After app runs, test with curl or /docs

### Task 28: CREATE `app/api/v1/router.py`

- **ACTION**: Create API v1 router aggregator
- **IMPLEMENT**:
  ```python
  from fastapi import APIRouter
  from app.api.v1 import auth, users, health

  router = APIRouter()
  router.include_router(health.router)
  router.include_router(auth.router, prefix="/auth", tags=["auth"])
  router.include_router(users.router, prefix="/users", tags=["users"])
  ```
- **VALIDATE**: `python -c "from app.api.v1.router import router"`

### Task 29: CREATE `app/main.py`

- **ACTION**: Create FastAPI application entry point
- **IMPLEMENT**:
  - Create FastAPI app with title, version, docs_url configuration
  - Add CORS middleware
  - Include API v1 router
  - Add startup/shutdown events if needed
- **VALIDATE**: `uvicorn app.main:app --reload` and check `/docs`

### Task 30: CREATE `alembic.ini`

- **ACTION**: Create Alembic configuration
- **IMPLEMENT**: Standard alembic.ini pointing to app/migrations
- **GOTCHA**: Set `sqlalchemy.url` to empty, will be set in env.py from config
- **VALIDATE**: File exists

### Task 31: CREATE `app/migrations/env.py`

- **ACTION**: Create async Alembic migration environment
- **IMPLEMENT**:
  - Import models to register with metadata
  - Configure async engine for migrations
  - Use `run_async_migrations()` pattern
- **GOTCHA**: Must import all models before running migrations
- **VALIDATE**: `alembic check`

### Task 32: CREATE `app/migrations/script.py.mako`

- **ACTION**: Create Alembic migration template
- **IMPLEMENT**: Standard Mako template for migrations
- **VALIDATE**: File exists

### Task 33: CREATE initial migration

- **ACTION**: Generate initial database migration
- **IMPLEMENT**: `alembic revision --autogenerate -m "initial_user_table"`
- **VALIDATE**: Migration file created in `app/migrations/versions/`

### Task 34: CREATE `tests/__init__.py`

- **ACTION**: Create tests package init
- **IMPLEMENT**: Empty file
- **VALIDATE**: `python -c "import tests"`

### Task 35: CREATE `tests/conftest.py`

- **ACTION**: Create pytest fixtures for async testing
- **IMPLEMENT**:
  - `async_client` fixture for API testing
  - `test_db` fixture for database testing
  - `test_user` fixture for authenticated tests
- **VALIDATE**: `pytest --collect-only`

### Task 36: CREATE `tests/test_auth.py`

- **ACTION**: Create authentication endpoint tests
- **IMPLEMENT**:
  - Test user registration success
  - Test registration with existing email (conflict)
  - Test login success
  - Test login with wrong password
  - Test token refresh
- **VALIDATE**: `pytest tests/test_auth.py -v`

### Task 37: CREATE `tests/test_users.py`

- **ACTION**: Create user endpoint tests
- **IMPLEMENT**:
  - Test get current user
  - Test update current user
  - Test admin list users
  - Test admin delete user
  - Test non-admin access denied
- **VALIDATE**: `pytest tests/test_users.py -v`

---

## Testing Strategy

### Unit Tests to Write

| Test File            | Test Cases                                           | Validates            |
| -------------------- | ---------------------------------------------------- | -------------------- |
| `tests/test_auth.py` | register, login, refresh, invalid credentials        | Auth endpoints       |
| `tests/test_users.py`| get_me, update_me, list (admin), delete (admin)      | User CRUD            |

### Edge Cases Checklist

- [ ] Empty email/password on registration
- [ ] Invalid email format
- [ ] Password too short (< 8 chars)
- [ ] Login with non-existent email
- [ ] Login with wrong password
- [ ] Expired access token
- [ ] Invalid refresh token
- [ ] Accessing admin routes as regular user
- [ ] Deleting self as admin
- [ ] Updating with duplicate email

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
ruff check . && mypy app --ignore-missing-imports
```

**EXPECT**: Exit 0, no errors

### Level 2: UNIT_TESTS

```bash
pytest tests/ -v --tb=short
```

**EXPECT**: All tests pass

### Level 3: FULL_SUITE

```bash
pytest tests/ -v && ruff check . && mypy app --ignore-missing-imports
```

**EXPECT**: All pass

### Level 4: DATABASE_VALIDATION

```bash
docker compose up -d db && sleep 5 && alembic upgrade head && alembic check
```

**EXPECT**: Migrations apply successfully

### Level 5: INTEGRATION_VALIDATION

```bash
docker compose up -d && sleep 10 && curl -f http://localhost:8000/api/v1/health
```

**EXPECT**: Health check returns 200

### Level 6: MANUAL_VALIDATION

1. Start services: `docker compose up`
2. Open http://localhost:8000/docs
3. Register a new user via `/auth/register`
4. Login via `/auth/login` to get tokens
5. Use "Authorize" button with Bearer token
6. Access `/users/me` to verify authentication
7. Test all CRUD operations

---

## Acceptance Criteria

- [ ] All 37 tasks completed in order
- [ ] Docker Compose starts PostgreSQL with pgvector and FastAPI app
- [ ] User registration with email/password works
- [ ] Login returns JWT access and refresh tokens
- [ ] Protected endpoints require valid JWT
- [ ] Admin-only endpoints reject non-admin users
- [ ] All validation commands pass
- [ ] API documentation available at `/docs`
- [ ] Health check endpoint responds
- [ ] Database migrations work correctly

---

## Completion Checklist

- [ ] All tasks completed in dependency order
- [ ] Each task validated immediately after completion
- [ ] Level 1: Static analysis (ruff + mypy) passes
- [ ] Level 2: Unit tests pass
- [ ] Level 3: Full test suite succeeds
- [ ] Level 4: Database migrations work
- [ ] Level 5: Docker integration works
- [ ] Level 6: Manual validation complete
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk                                | Likelihood | Impact | Mitigation                                           |
| ----------------------------------- | ---------- | ------ | ---------------------------------------------------- |
| pwdlib API changes from passlib     | LOW        | MED    | Pin version, test password hashing early             |
| SQLAlchemy async session issues     | MED        | HIGH   | Use `expire_on_commit=False`, proper exception handling |
| pgvector extension not loaded       | LOW        | HIGH   | Use `pgvector/pgvector:pg17` image, test early       |
| JWT token security misconfiguration | MED        | HIGH   | Use strong secret key, proper expiration times       |
| Docker networking between services  | LOW        | MED    | Use service names, health checks, depends_on         |

---

## Notes

### Design Decisions

1. **pwdlib over passlib**: passlib is unmaintained since 2020 and has compatibility issues with bcrypt 5.x. pwdlib is the modern replacement recommended for FastAPI.

2. **Argon2 over bcrypt**: OWASP 2025 recommends Argon2id as the gold standard. bcrypt has a 72-byte password limit and is potentially vulnerable to FPGA attacks.

3. **Repository + Service pattern**: Separates database operations from business logic, making code testable and maintainable.

4. **expire_on_commit=False**: Critical for async SQLAlchemy to prevent detached object issues when accessing model attributes after commit.

5. **pgvector included**: Vector column type registered in SQLAlchemy for future AI/ML features, even if not used in initial user module.

### Future Considerations

- Add email verification with background task queue
- Implement OAuth2 social login providers
- Add rate limiting with slowapi
- Implement Redis caching for sessions
- Add comprehensive logging with structlog
- Implement API key authentication for service-to-service calls

### External Documentation

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy 2.0 Async Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [pgvector Python](https://github.com/pgvector/pgvector-python)
- [pwdlib Documentation](https://github.com/frankie567/pwdlib)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
