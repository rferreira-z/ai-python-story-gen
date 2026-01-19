# Feature: Multi-Tenant Story Universe and Stories

## Summary

Implement two new multi-tenant entities: **StoryUniverse** (for managing story world details with markdown descriptions) and **Story** (for managing stories with text content and image URLs). Both entities use `user_id` as the tenant identifier for data isolation. Stories belong to a StoryUniverse via foreign key relationship.

## User Story

As an authenticated user
I want to create and manage story universes with markdown descriptions, and stories with text content and image URLs
So that I can organize my creative writing content in isolated, personal workspaces

## Problem Statement

The application currently only supports user management. Users need the ability to:
1. Create "story universes" - fictional worlds with detailed markdown descriptions
2. Create "stories" within those universes containing narrative text and associated images
3. Have complete data isolation - users can only see/modify their own content

## Solution Statement

Add two new database entities following the existing layered architecture (Model → Repository → Service → API). Both entities implement multi-tenancy via `user_id` foreign key. StoryUniverse stores large markdown text, Story stores narrative text plus an array of image URLs. Full CRUD operations exposed via REST API endpoints.

## Metadata

| Field            | Value                                                |
| ---------------- | ---------------------------------------------------- |
| Type             | NEW_CAPABILITY                                       |
| Complexity       | MEDIUM                                               |
| Systems Affected | models, schemas, repositories, services, api, tests  |
| Dependencies     | SQLAlchemy>=2.0.36, asyncpg>=0.30.0, pydantic>=2.10  |
| Estimated Tasks  | 16                                                   |

---

## UX Design

### Before State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              BEFORE STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐            ║
║   │   User      │ ──────► │   Login     │ ──────► │   Profile   │            ║
║   │  Register   │         │   /auth     │         │   /users/me │            ║
║   └─────────────┘         └─────────────┘         └─────────────┘            ║
║                                                                               ║
║   USER_FLOW: Register → Login → View Profile (no content management)          ║
║   PAIN_POINT: No way to store creative writing content                        ║
║   DATA_FLOW: User credentials → JWT token → Profile data                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### After State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                               AFTER STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐            ║
║   │   User      │ ──────► │   Login     │ ──────► │   Profile   │            ║
║   │  Register   │         │   /auth     │         │   /users/me │            ║
║   └─────────────┘         └─────────────┘         └──────┬──────┘            ║
║                                                          │                    ║
║                                                          ▼                    ║
║                                                 ┌─────────────────┐           ║
║                                                 │ Story Universes │           ║
║                                                 │ /story-universes│           ║
║                                                 └────────┬────────┘           ║
║                                                          │                    ║
║                                                          ▼                    ║
║                                                 ┌─────────────────┐           ║
║                                                 │    Stories      │           ║
║                                                 │    /stories     │           ║
║                                                 └─────────────────┘           ║
║                                                                               ║
║   USER_FLOW: Login → Create Universe → Create Stories → View/Edit/Delete      ║
║   VALUE_ADD: Full content management with multi-tenancy isolation             ║
║   DATA_FLOW: JWT → user_id extraction → tenant-scoped queries                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Interaction Changes

| Location              | Before             | After                           | User Impact                              |
|-----------------------|--------------------|---------------------------------|------------------------------------------|
| `/api/v1/story-universes` | Does not exist | CRUD for story universes        | Users can create fictional worlds        |
| `/api/v1/stories`         | Does not exist | CRUD for stories                | Users can write and manage stories       |
| Database                  | Only users table | users + story_universes + stories | Persistent content storage             |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `app/models/user.py` | all | Model pattern to MIRROR exactly |
| P0 | `app/repositories/user.py` | all | Repository pattern to MIRROR |
| P0 | `app/services/user.py` | all | Service pattern to MIRROR |
| P0 | `app/api/v1/users.py` | all | API route pattern to MIRROR |
| P0 | `app/api/deps.py` | all | Dependency injection pattern |
| P1 | `app/schemas/user.py` | all | Pydantic schema pattern |
| P1 | `app/core/exceptions.py` | all | Custom exception classes |
| P2 | `tests/conftest.py` | all | Test fixture patterns |
| P2 | `tests/test_users.py` | all | Test assertion patterns |
| P2 | `app/migrations/env.py` | all | Migration setup for model imports |

**External Documentation:**

| Source | Section | Why Needed |
|--------|---------|------------|
| [SQLAlchemy 2.0 Type Basics](https://docs.sqlalchemy.org/en/20/core/type_basics.html) | Text type | Large text column for markdown/content |
| [SQLAlchemy PostgreSQL ARRAY](https://www.fullstackpython.com/sqlalchemy-dialects-postgresql-array-examples.html) | ARRAY type | Storing image URLs as array |

---

## Patterns to Mirror

**MODEL_PATTERN:**
```python
# SOURCE: app/models/user.py:1-22
# COPY THIS PATTERN:
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # ... fields ...
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

**SCHEMA_PATTERN:**
```python
# SOURCE: app/schemas/user.py:1-40
# COPY THIS PATTERN:
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    email: EmailStr | None = None
    full_name: str | None = None

class UserResponse(BaseModel):
    """Schema for user response data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime
```

**REPOSITORY_PATTERN:**
```python
# SOURCE: app/repositories/user.py:1-40
# COPY THIS PATTERN:
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
```

**SERVICE_PATTERN:**
```python
# SOURCE: app/services/user.py:1-35
# COPY THIS PATTERN:
from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.user import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_by_id(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User with id {user_id} not found")
        return user
```

**API_ROUTE_PATTERN:**
```python
# SOURCE: app/api/v1/users.py:1-30
# COPY THIS PATTERN:
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_active_user, get_user_service
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
```

**TEST_PATTERN:**
```python
# SOURCE: tests/test_users.py:1-20
# COPY THIS PATTERN:
import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, test_user: User, user_token: str):
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
```

---

## Files to Change

| File                                      | Action | Justification                                |
|-------------------------------------------|--------|----------------------------------------------|
| `app/models/story_universe.py`            | CREATE | StoryUniverse SQLAlchemy model               |
| `app/models/story.py`                     | CREATE | Story SQLAlchemy model                       |
| `app/models/__init__.py`                  | UPDATE | Export new models                            |
| `app/schemas/story_universe.py`           | CREATE | Pydantic schemas for StoryUniverse           |
| `app/schemas/story.py`                    | CREATE | Pydantic schemas for Story                   |
| `app/schemas/__init__.py`                 | UPDATE | Export new schemas                           |
| `app/repositories/story_universe.py`      | CREATE | StoryUniverse repository                     |
| `app/repositories/story.py`               | CREATE | Story repository                             |
| `app/repositories/__init__.py`            | UPDATE | Export new repositories                      |
| `app/services/story_universe.py`          | CREATE | StoryUniverse service                        |
| `app/services/story.py`                   | CREATE | Story service                                |
| `app/services/__init__.py`                | UPDATE | Export new services                          |
| `app/api/deps.py`                         | UPDATE | Add dependency injection for new services    |
| `app/api/v1/story_universes.py`           | CREATE | StoryUniverse API endpoints                  |
| `app/api/v1/stories.py`                   | CREATE | Story API endpoints                          |
| `app/api/v1/router.py`                    | UPDATE | Include new routers                          |
| `app/migrations/env.py`                   | UPDATE | Import new models for Alembic                |
| `tests/test_story_universes.py`           | CREATE | StoryUniverse tests                          |
| `tests/test_stories.py`                   | CREATE | Story tests                                  |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- **Image upload/storage** - Only storing URLs, not actual image files
- **Story versioning** - No version history for story content
- **Collaborative editing** - Stories are single-user only (tenant isolation)
- **Search functionality** - No full-text search on story content
- **Story publishing/sharing** - All content is private to the owner
- **Rich text editor** - Content is plain markdown/text stored as-is
- **Nested universes** - No hierarchy, universes are flat
- **Story ordering** - No explicit ordering within a universe

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

### Task 1: CREATE `app/models/story_universe.py`

- **ACTION**: CREATE new model file
- **IMPLEMENT**:
  ```python
  from datetime import datetime
  from sqlalchemy import DateTime, ForeignKey, String, Text, func
  from sqlalchemy.orm import Mapped, mapped_column
  from app.core.database import Base

  class StoryUniverse(Base):
      """Story Universe model for managing fictional worlds."""
      __tablename__ = "story_universes"

      id: Mapped[int] = mapped_column(primary_key=True)
      user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
      name: Mapped[str] = mapped_column(String(255))
      description: Mapped[str | None] = mapped_column(Text, nullable=True)
      created_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True), server_default=func.now()
      )
      updated_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
      )
  ```
- **MIRROR**: `app/models/user.py` - follow existing model pattern
- **IMPORTS**: `from sqlalchemy import DateTime, ForeignKey, String, Text, func`
- **GOTCHA**: Use `Text` (not `String`) for large markdown content
- **VALIDATE**: `ruff check app/models/story_universe.py && mypy app/models/story_universe.py`

### Task 2: CREATE `app/models/story.py`

- **ACTION**: CREATE new model file
- **IMPLEMENT**:
  ```python
  from datetime import datetime
  from sqlalchemy import DateTime, ForeignKey, String, Text, func
  from sqlalchemy.dialects.postgresql import ARRAY
  from sqlalchemy.orm import Mapped, mapped_column
  from app.core.database import Base

  class Story(Base):
      """Story model for managing narrative content."""
      __tablename__ = "stories"

      id: Mapped[int] = mapped_column(primary_key=True)
      user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
      story_universe_id: Mapped[int] = mapped_column(
          ForeignKey("story_universes.id"), index=True
      )
      title: Mapped[str] = mapped_column(String(255))
      content: Mapped[str | None] = mapped_column(Text, nullable=True)
      image_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
      created_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True), server_default=func.now()
      )
      updated_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
      )
  ```
- **MIRROR**: `app/models/user.py` - follow existing model pattern
- **IMPORTS**: `from sqlalchemy.dialects.postgresql import ARRAY`
- **GOTCHA**: ARRAY requires PostgreSQL - use `from sqlalchemy.dialects.postgresql import ARRAY`
- **VALIDATE**: `ruff check app/models/story.py && mypy app/models/story.py`

### Task 3: UPDATE `app/models/__init__.py`

- **ACTION**: UPDATE to export new models
- **IMPLEMENT**: Add imports for StoryUniverse and Story
- **MIRROR**: Current file structure with User export
- **VALIDATE**: `ruff check app/models/__init__.py`

### Task 4: CREATE `app/schemas/story_universe.py`

- **ACTION**: CREATE Pydantic schemas
- **IMPLEMENT**:
  ```python
  from datetime import datetime
  from pydantic import BaseModel, ConfigDict, Field

  class StoryUniverseCreate(BaseModel):
      """Schema for creating a story universe."""
      name: str = Field(min_length=1, max_length=255)
      description: str | None = None

  class StoryUniverseUpdate(BaseModel):
      """Schema for updating a story universe."""
      name: str | None = Field(default=None, min_length=1, max_length=255)
      description: str | None = None

  class StoryUniverseResponse(BaseModel):
      """Schema for story universe response."""
      model_config = ConfigDict(from_attributes=True)

      id: int
      user_id: int
      name: str
      description: str | None
      created_at: datetime
      updated_at: datetime
  ```
- **MIRROR**: `app/schemas/user.py` - follow Create/Update/Response pattern
- **GOTCHA**: Use `Field(min_length=1)` to prevent empty strings
- **VALIDATE**: `ruff check app/schemas/story_universe.py && mypy app/schemas/story_universe.py`

### Task 5: CREATE `app/schemas/story.py`

- **ACTION**: CREATE Pydantic schemas
- **IMPLEMENT**:
  ```python
  from datetime import datetime
  from pydantic import BaseModel, ConfigDict, Field

  class StoryCreate(BaseModel):
      """Schema for creating a story."""
      story_universe_id: int
      title: str = Field(min_length=1, max_length=255)
      content: str | None = None
      image_urls: list[str] | None = None

  class StoryUpdate(BaseModel):
      """Schema for updating a story."""
      title: str | None = Field(default=None, min_length=1, max_length=255)
      content: str | None = None
      image_urls: list[str] | None = None

  class StoryResponse(BaseModel):
      """Schema for story response."""
      model_config = ConfigDict(from_attributes=True)

      id: int
      user_id: int
      story_universe_id: int
      title: str
      content: str | None
      image_urls: list[str] | None
      created_at: datetime
      updated_at: datetime
  ```
- **MIRROR**: `app/schemas/user.py`
- **GOTCHA**: `image_urls` as `list[str] | None` matches ARRAY column
- **VALIDATE**: `ruff check app/schemas/story.py && mypy app/schemas/story.py`

### Task 6: UPDATE `app/schemas/__init__.py`

- **ACTION**: UPDATE to export new schemas
- **IMPLEMENT**: Add imports for StoryUniverse and Story schemas
- **VALIDATE**: `ruff check app/schemas/__init__.py`

### Task 7: CREATE `app/repositories/story_universe.py`

- **ACTION**: CREATE repository with CRUD operations
- **IMPLEMENT**:
  ```python
  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.models.story_universe import StoryUniverse

  class StoryUniverseRepository:
      """Repository for StoryUniverse database operations."""

      def __init__(self, session: AsyncSession):
          self.session = session

      async def get_by_id(self, universe_id: int) -> StoryUniverse | None:
          result = await self.session.execute(
              select(StoryUniverse).where(StoryUniverse.id == universe_id)
          )
          return result.scalar_one_or_none()

      async def get_by_user_and_id(
          self, user_id: int, universe_id: int
      ) -> StoryUniverse | None:
          result = await self.session.execute(
              select(StoryUniverse).where(
                  StoryUniverse.id == universe_id,
                  StoryUniverse.user_id == user_id
              )
          )
          return result.scalar_one_or_none()

      async def get_all_by_user(
          self, user_id: int, skip: int = 0, limit: int = 100
      ) -> list[StoryUniverse]:
          result = await self.session.execute(
              select(StoryUniverse)
              .where(StoryUniverse.user_id == user_id)
              .offset(skip)
              .limit(limit)
          )
          return list(result.scalars().all())

      async def create(self, universe: StoryUniverse) -> StoryUniverse:
          self.session.add(universe)
          await self.session.flush()
          await self.session.refresh(universe)
          return universe

      async def update(
          self, universe: StoryUniverse, update_data: dict
      ) -> StoryUniverse:
          for field, value in update_data.items():
              if value is not None:
                  setattr(universe, field, value)
          await self.session.flush()
          await self.session.refresh(universe)
          return universe

      async def delete(self, universe: StoryUniverse) -> None:
          await self.session.delete(universe)
          await self.session.flush()
  ```
- **MIRROR**: `app/repositories/user.py`
- **GOTCHA**: `get_by_user_and_id` is the key multi-tenant query pattern
- **VALIDATE**: `ruff check app/repositories/story_universe.py && mypy app/repositories/story_universe.py`

### Task 8: CREATE `app/repositories/story.py`

- **ACTION**: CREATE repository with CRUD operations
- **IMPLEMENT**:
  ```python
  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.models.story import Story

  class StoryRepository:
      """Repository for Story database operations."""

      def __init__(self, session: AsyncSession):
          self.session = session

      async def get_by_id(self, story_id: int) -> Story | None:
          result = await self.session.execute(
              select(Story).where(Story.id == story_id)
          )
          return result.scalar_one_or_none()

      async def get_by_user_and_id(self, user_id: int, story_id: int) -> Story | None:
          result = await self.session.execute(
              select(Story).where(Story.id == story_id, Story.user_id == user_id)
          )
          return result.scalar_one_or_none()

      async def get_all_by_user(
          self, user_id: int, skip: int = 0, limit: int = 100
      ) -> list[Story]:
          result = await self.session.execute(
              select(Story)
              .where(Story.user_id == user_id)
              .offset(skip)
              .limit(limit)
          )
          return list(result.scalars().all())

      async def get_all_by_universe(
          self, user_id: int, universe_id: int, skip: int = 0, limit: int = 100
      ) -> list[Story]:
          result = await self.session.execute(
              select(Story)
              .where(Story.user_id == user_id, Story.story_universe_id == universe_id)
              .offset(skip)
              .limit(limit)
          )
          return list(result.scalars().all())

      async def create(self, story: Story) -> Story:
          self.session.add(story)
          await self.session.flush()
          await self.session.refresh(story)
          return story

      async def update(self, story: Story, update_data: dict) -> Story:
          for field, value in update_data.items():
              if value is not None:
                  setattr(story, field, value)
          await self.session.flush()
          await self.session.refresh(story)
          return story

      async def delete(self, story: Story) -> None:
          await self.session.delete(story)
          await self.session.flush()
  ```
- **MIRROR**: `app/repositories/user.py`
- **GOTCHA**: Include `get_all_by_universe` for filtered story lists
- **VALIDATE**: `ruff check app/repositories/story.py && mypy app/repositories/story.py`

### Task 9: UPDATE `app/repositories/__init__.py`

- **ACTION**: UPDATE to export new repositories
- **IMPLEMENT**: Add imports for StoryUniverseRepository and StoryRepository
- **VALIDATE**: `ruff check app/repositories/__init__.py`

### Task 10: CREATE `app/services/story_universe.py`

- **ACTION**: CREATE service with business logic
- **IMPLEMENT**:
  ```python
  from app.core.exceptions import NotFoundError
  from app.models.story_universe import StoryUniverse
  from app.repositories.story_universe import StoryUniverseRepository
  from app.schemas.story_universe import StoryUniverseCreate, StoryUniverseUpdate

  class StoryUniverseService:
      """Service for StoryUniverse business logic."""

      def __init__(self, repository: StoryUniverseRepository):
          self.repository = repository

      async def get_by_id(self, user_id: int, universe_id: int) -> StoryUniverse:
          universe = await self.repository.get_by_user_and_id(user_id, universe_id)
          if universe is None:
              raise NotFoundError(f"Story universe with id {universe_id} not found")
          return universe

      async def get_all(
          self, user_id: int, skip: int = 0, limit: int = 100
      ) -> list[StoryUniverse]:
          return await self.repository.get_all_by_user(user_id, skip=skip, limit=limit)

      async def create(
          self, user_id: int, data: StoryUniverseCreate
      ) -> StoryUniverse:
          universe = StoryUniverse(
              user_id=user_id,
              name=data.name,
              description=data.description,
          )
          return await self.repository.create(universe)

      async def update(
          self, user_id: int, universe_id: int, data: StoryUniverseUpdate
      ) -> StoryUniverse:
          universe = await self.get_by_id(user_id, universe_id)
          update_data = data.model_dump(exclude_unset=True)
          return await self.repository.update(universe, update_data)

      async def delete(self, user_id: int, universe_id: int) -> None:
          universe = await self.get_by_id(user_id, universe_id)
          await self.repository.delete(universe)
  ```
- **MIRROR**: `app/services/user.py`
- **GOTCHA**: All methods take `user_id` for tenant isolation
- **VALIDATE**: `ruff check app/services/story_universe.py && mypy app/services/story_universe.py`

### Task 11: CREATE `app/services/story.py`

- **ACTION**: CREATE service with business logic
- **IMPLEMENT**:
  ```python
  from app.core.exceptions import NotFoundError
  from app.models.story import Story
  from app.repositories.story import StoryRepository
  from app.repositories.story_universe import StoryUniverseRepository
  from app.schemas.story import StoryCreate, StoryUpdate

  class StoryService:
      """Service for Story business logic."""

      def __init__(
          self,
          repository: StoryRepository,
          universe_repository: StoryUniverseRepository,
      ):
          self.repository = repository
          self.universe_repository = universe_repository

      async def get_by_id(self, user_id: int, story_id: int) -> Story:
          story = await self.repository.get_by_user_and_id(user_id, story_id)
          if story is None:
              raise NotFoundError(f"Story with id {story_id} not found")
          return story

      async def get_all(
          self, user_id: int, skip: int = 0, limit: int = 100
      ) -> list[Story]:
          return await self.repository.get_all_by_user(user_id, skip=skip, limit=limit)

      async def get_all_by_universe(
          self, user_id: int, universe_id: int, skip: int = 0, limit: int = 100
      ) -> list[Story]:
          # Verify universe exists and belongs to user
          universe = await self.universe_repository.get_by_user_and_id(
              user_id, universe_id
          )
          if universe is None:
              raise NotFoundError(f"Story universe with id {universe_id} not found")
          return await self.repository.get_all_by_universe(
              user_id, universe_id, skip=skip, limit=limit
          )

      async def create(self, user_id: int, data: StoryCreate) -> Story:
          # Verify universe exists and belongs to user
          universe = await self.universe_repository.get_by_user_and_id(
              user_id, data.story_universe_id
          )
          if universe is None:
              raise NotFoundError(
                  f"Story universe with id {data.story_universe_id} not found"
              )

          story = Story(
              user_id=user_id,
              story_universe_id=data.story_universe_id,
              title=data.title,
              content=data.content,
              image_urls=data.image_urls,
          )
          return await self.repository.create(story)

      async def update(
          self, user_id: int, story_id: int, data: StoryUpdate
      ) -> Story:
          story = await self.get_by_id(user_id, story_id)
          update_data = data.model_dump(exclude_unset=True)
          return await self.repository.update(story, update_data)

      async def delete(self, user_id: int, story_id: int) -> None:
          story = await self.get_by_id(user_id, story_id)
          await self.repository.delete(story)
  ```
- **MIRROR**: `app/services/user.py`
- **GOTCHA**: Verify universe ownership before creating/listing stories in that universe
- **VALIDATE**: `ruff check app/services/story.py && mypy app/services/story.py`

### Task 12: UPDATE `app/services/__init__.py`

- **ACTION**: UPDATE to export new services
- **IMPLEMENT**: Add imports for StoryUniverseService and StoryService
- **VALIDATE**: `ruff check app/services/__init__.py`

### Task 13: UPDATE `app/api/deps.py`

- **ACTION**: ADD dependency injection for new services
- **IMPLEMENT**: Add the following functions:
  ```python
  from app.repositories.story_universe import StoryUniverseRepository
  from app.repositories.story import StoryRepository
  from app.services.story_universe import StoryUniverseService
  from app.services.story import StoryService

  async def get_story_universe_repository(
      db: Annotated[AsyncSession, Depends(get_db)],
  ) -> StoryUniverseRepository:
      return StoryUniverseRepository(db)

  async def get_story_repository(
      db: Annotated[AsyncSession, Depends(get_db)],
  ) -> StoryRepository:
      return StoryRepository(db)

  async def get_story_universe_service(
      repo: Annotated[StoryUniverseRepository, Depends(get_story_universe_repository)],
  ) -> StoryUniverseService:
      return StoryUniverseService(repo)

  async def get_story_service(
      repo: Annotated[StoryRepository, Depends(get_story_repository)],
      universe_repo: Annotated[
          StoryUniverseRepository, Depends(get_story_universe_repository)
      ],
  ) -> StoryService:
      return StoryService(repo, universe_repo)
  ```
- **MIRROR**: Existing `get_user_repository` and `get_user_service` patterns
- **GOTCHA**: StoryService needs both StoryRepository AND StoryUniverseRepository
- **VALIDATE**: `ruff check app/api/deps.py && mypy app/api/deps.py`

### Task 14: CREATE `app/api/v1/story_universes.py`

- **ACTION**: CREATE API endpoints for StoryUniverse
- **IMPLEMENT**:
  ```python
  from typing import Annotated
  from fastapi import APIRouter, Depends, Query, status
  from app.api.deps import get_current_active_user, get_story_universe_service
  from app.models.user import User
  from app.schemas.story_universe import (
      StoryUniverseCreate,
      StoryUniverseResponse,
      StoryUniverseUpdate,
  )
  from app.services.story_universe import StoryUniverseService

  router = APIRouter()

  @router.post("", response_model=StoryUniverseResponse, status_code=status.HTTP_201_CREATED)
  async def create_story_universe(
      data: StoryUniverseCreate,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryUniverseService, Depends(get_story_universe_service)],
  ) -> StoryUniverseResponse:
      """Create a new story universe."""
      universe = await service.create(current_user.id, data)
      return StoryUniverseResponse.model_validate(universe)

  @router.get("", response_model=list[StoryUniverseResponse])
  async def list_story_universes(
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryUniverseService, Depends(get_story_universe_service)],
      skip: int = Query(default=0, ge=0),
      limit: int = Query(default=100, ge=1, le=1000),
  ) -> list[StoryUniverseResponse]:
      """List all story universes for the current user."""
      universes = await service.get_all(current_user.id, skip=skip, limit=limit)
      return [StoryUniverseResponse.model_validate(u) for u in universes]

  @router.get("/{universe_id}", response_model=StoryUniverseResponse)
  async def get_story_universe(
      universe_id: int,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryUniverseService, Depends(get_story_universe_service)],
  ) -> StoryUniverseResponse:
      """Get a story universe by ID."""
      universe = await service.get_by_id(current_user.id, universe_id)
      return StoryUniverseResponse.model_validate(universe)

  @router.put("/{universe_id}", response_model=StoryUniverseResponse)
  async def update_story_universe(
      universe_id: int,
      data: StoryUniverseUpdate,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryUniverseService, Depends(get_story_universe_service)],
  ) -> StoryUniverseResponse:
      """Update a story universe."""
      universe = await service.update(current_user.id, universe_id, data)
      return StoryUniverseResponse.model_validate(universe)

  @router.delete("/{universe_id}", status_code=status.HTTP_204_NO_CONTENT)
  async def delete_story_universe(
      universe_id: int,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryUniverseService, Depends(get_story_universe_service)],
  ) -> None:
      """Delete a story universe."""
      await service.delete(current_user.id, universe_id)
  ```
- **MIRROR**: `app/api/v1/users.py`
- **GOTCHA**: Use `status.HTTP_201_CREATED` for POST, `status.HTTP_204_NO_CONTENT` for DELETE
- **VALIDATE**: `ruff check app/api/v1/story_universes.py && mypy app/api/v1/story_universes.py`

### Task 15: CREATE `app/api/v1/stories.py`

- **ACTION**: CREATE API endpoints for Story
- **IMPLEMENT**:
  ```python
  from typing import Annotated
  from fastapi import APIRouter, Depends, Query, status
  from app.api.deps import get_current_active_user, get_story_service
  from app.models.user import User
  from app.schemas.story import StoryCreate, StoryResponse, StoryUpdate
  from app.services.story import StoryService

  router = APIRouter()

  @router.post("", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
  async def create_story(
      data: StoryCreate,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryService, Depends(get_story_service)],
  ) -> StoryResponse:
      """Create a new story."""
      story = await service.create(current_user.id, data)
      return StoryResponse.model_validate(story)

  @router.get("", response_model=list[StoryResponse])
  async def list_stories(
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryService, Depends(get_story_service)],
      universe_id: int | None = Query(default=None),
      skip: int = Query(default=0, ge=0),
      limit: int = Query(default=100, ge=1, le=1000),
  ) -> list[StoryResponse]:
      """List all stories for the current user, optionally filtered by universe."""
      if universe_id is not None:
          stories = await service.get_all_by_universe(
              current_user.id, universe_id, skip=skip, limit=limit
          )
      else:
          stories = await service.get_all(current_user.id, skip=skip, limit=limit)
      return [StoryResponse.model_validate(s) for s in stories]

  @router.get("/{story_id}", response_model=StoryResponse)
  async def get_story(
      story_id: int,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryService, Depends(get_story_service)],
  ) -> StoryResponse:
      """Get a story by ID."""
      story = await service.get_by_id(current_user.id, story_id)
      return StoryResponse.model_validate(story)

  @router.put("/{story_id}", response_model=StoryResponse)
  async def update_story(
      story_id: int,
      data: StoryUpdate,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryService, Depends(get_story_service)],
  ) -> StoryResponse:
      """Update a story."""
      story = await service.update(current_user.id, story_id, data)
      return StoryResponse.model_validate(story)

  @router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
  async def delete_story(
      story_id: int,
      current_user: Annotated[User, Depends(get_current_active_user)],
      service: Annotated[StoryService, Depends(get_story_service)],
  ) -> None:
      """Delete a story."""
      await service.delete(current_user.id, story_id)
  ```
- **MIRROR**: `app/api/v1/users.py`
- **GOTCHA**: Optional `universe_id` query param for filtering stories
- **VALIDATE**: `ruff check app/api/v1/stories.py && mypy app/api/v1/stories.py`

### Task 16: UPDATE `app/api/v1/router.py`

- **ACTION**: UPDATE to include new routers
- **IMPLEMENT**: Add router includes:
  ```python
  from app.api.v1 import story_universes, stories

  router.include_router(
      story_universes.router, prefix="/story-universes", tags=["story-universes"]
  )
  router.include_router(stories.router, prefix="/stories", tags=["stories"])
  ```
- **MIRROR**: Existing router.include_router patterns
- **VALIDATE**: `ruff check app/api/v1/router.py`

### Task 17: UPDATE `app/migrations/env.py`

- **ACTION**: UPDATE to import new models for Alembic
- **IMPLEMENT**: Add imports:
  ```python
  from app.models import User, StoryUniverse, Story  # noqa: F401
  ```
- **MIRROR**: Existing model import pattern
- **VALIDATE**: `ruff check app/migrations/env.py`

### Task 18: GENERATE database migration

- **ACTION**: Run Alembic to generate migration
- **IMPLEMENT**: `alembic revision --autogenerate -m "add story_universes and stories tables"`
- **GOTCHA**: Review generated migration for correct foreign keys and indexes
- **VALIDATE**: Review migration file, then `alembic upgrade head` (on test DB)

### Task 19: CREATE `tests/test_story_universes.py`

- **ACTION**: CREATE tests for StoryUniverse endpoints
- **IMPLEMENT**: Tests for create, list, get, update, delete + auth + not found
- **MIRROR**: `tests/test_users.py` patterns
- **VALIDATE**: `pytest tests/test_story_universes.py -v`

### Task 20: CREATE `tests/test_stories.py`

- **ACTION**: CREATE tests for Story endpoints
- **IMPLEMENT**: Tests for create, list, get, update, delete + universe filtering + auth
- **MIRROR**: `tests/test_users.py` patterns
- **VALIDATE**: `pytest tests/test_stories.py -v`

---

## Testing Strategy

### Unit Tests to Write

| Test File | Test Cases | Validates |
|-----------|------------|-----------|
| `tests/test_story_universes.py` | create, list, get, update, delete, not_found, unauthorized | StoryUniverse CRUD + auth |
| `tests/test_stories.py` | create, list, list_by_universe, get, update, delete, invalid_universe, not_found | Story CRUD + filtering |

### Edge Cases Checklist

- [ ] Create story universe with empty name (should fail - validation)
- [ ] Create story in non-existent universe (should fail - NotFoundError)
- [ ] Create story in another user's universe (should fail - NotFoundError)
- [ ] Get another user's story universe (should fail - NotFoundError)
- [ ] Get another user's story (should fail - NotFoundError)
- [ ] Update with partial data (should work - exclude_unset)
- [ ] Delete story universe with stories (cascading behavior)
- [ ] List stories filtered by universe_id
- [ ] Pagination (skip/limit parameters)

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

```bash
ruff check app/ tests/ && mypy app/
```

**EXPECT**: Exit 0, no errors or warnings

### Level 2: UNIT_TESTS

```bash
pytest tests/ -v
```

**EXPECT**: All tests pass

### Level 3: FULL_SUITE

```bash
ruff check app/ tests/ && mypy app/ && pytest tests/ -v
```

**EXPECT**: All checks pass

### Level 4: DATABASE_VALIDATION

```bash
# Apply migration
alembic upgrade head

# Verify tables exist (requires running PostgreSQL)
# Or run the app and check /docs
```

**EXPECT**: Tables created with correct schema

### Level 5: MANUAL_VALIDATION

1. Start the server: `uvicorn app.main:app --reload`
2. Register a user via `/api/v1/auth/register`
3. Login via `/api/v1/auth/login` to get token
4. Create a story universe via POST `/api/v1/story-universes`
5. List story universes via GET `/api/v1/story-universes`
6. Create a story via POST `/api/v1/stories`
7. List stories via GET `/api/v1/stories`
8. List stories by universe via GET `/api/v1/stories?universe_id=1`
9. Update and delete operations

---

## Acceptance Criteria

- [ ] StoryUniverse and Story models created with correct schema
- [ ] Multi-tenant isolation works (users only see their own data)
- [ ] CRUD operations work for both entities
- [ ] Stories can be filtered by universe_id
- [ ] Story creation validates universe ownership
- [ ] All Level 1-3 validation commands pass
- [ ] Unit tests cover happy paths and error cases
- [ ] API documentation shows up in /docs (when debug=True)

---

## Completion Checklist

- [ ] All 20 tasks completed in dependency order
- [ ] Each task validated immediately after completion
- [ ] Level 1: Static analysis (ruff + mypy) passes
- [ ] Level 2: Unit tests pass
- [ ] Level 3: Full validation suite passes
- [ ] Level 4: Database migration applied successfully
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ARRAY type not supported in SQLite tests | HIGH | MEDIUM | Use PostgreSQL test container OR mock ARRAY as JSON in tests |
| Cascading delete issues when deleting universe with stories | MEDIUM | HIGH | Add ON DELETE CASCADE to foreign key OR handle in service layer |
| Large text content causing performance issues | LOW | MEDIUM | Lazy loading, pagination, consider chunked responses |

---

## Notes

- **Design Decision**: Using PostgreSQL ARRAY for image_urls instead of JSON or separate table for simplicity. If portability to other DBs is needed, switch to JSON type.
- **Design Decision**: Stories have `user_id` directly (denormalized) for simpler multi-tenant queries rather than joining through story_universe.
- **Future Consideration**: If story content becomes very large, consider separate storage (S3) with content_url reference.
- **Future Consideration**: Add full-text search indexes on story content/title if search is needed later.
