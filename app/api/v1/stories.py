"""Story CRUD endpoints."""

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
