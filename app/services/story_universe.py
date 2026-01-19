"""StoryUniverse service for business logic."""

from app.core.exceptions import NotFoundError
from app.models.story_universe import StoryUniverse
from app.repositories.story_universe import StoryUniverseRepository
from app.schemas.story_universe import StoryUniverseCreate, StoryUniverseUpdate


class StoryUniverseService:
    """Service for StoryUniverse business logic."""

    def __init__(self, repository: StoryUniverseRepository):
        self.repository = repository

    async def get_by_id(self, user_id: int, universe_id: int) -> StoryUniverse:
        """Get a story universe by ID, raises NotFoundError if not found."""
        universe = await self.repository.get_by_user_and_id(user_id, universe_id)
        if universe is None:
            raise NotFoundError(f"Story universe with id {universe_id} not found")
        return universe

    async def get_all(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[StoryUniverse]:
        """Get all story universes for a user with pagination."""
        return await self.repository.get_all_by_user(user_id, skip=skip, limit=limit)

    async def create(
        self, user_id: int, data: StoryUniverseCreate
    ) -> StoryUniverse:
        """Create a new story universe."""
        universe = StoryUniverse(
            user_id=user_id,
            name=data.name,
            description=data.description,
        )
        return await self.repository.create(universe)

    async def update(
        self, user_id: int, universe_id: int, data: StoryUniverseUpdate
    ) -> StoryUniverse:
        """Update a story universe."""
        universe = await self.get_by_id(user_id, universe_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repository.update(universe, update_data)

    async def delete(self, user_id: int, universe_id: int) -> None:
        """Delete a story universe."""
        universe = await self.get_by_id(user_id, universe_id)
        await self.repository.delete(universe)
