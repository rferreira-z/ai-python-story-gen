"""StoryUniverse CRUD endpoints."""

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


@router.post(
    "", response_model=StoryUniverseResponse, status_code=status.HTTP_201_CREATED
)
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
