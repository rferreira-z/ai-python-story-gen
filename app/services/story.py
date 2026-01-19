"""Story service for business logic."""

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
        """Get a story by ID, raises NotFoundError if not found."""
        story = await self.repository.get_by_user_and_id(user_id, story_id)
        if story is None:
            raise NotFoundError(f"Story with id {story_id} not found")
        return story

    async def get_all(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Story]:
        """Get all stories for a user with pagination."""
        return await self.repository.get_all_by_user(user_id, skip=skip, limit=limit)

    async def get_all_by_universe(
        self, user_id: int, universe_id: int, skip: int = 0, limit: int = 100
    ) -> list[Story]:
        """Get all stories in a universe for a user with pagination."""
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
        """Create a new story."""
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
        """Update a story."""
        story = await self.get_by_id(user_id, story_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repository.update(story, update_data)

    async def delete(self, user_id: int, story_id: int) -> None:
        """Delete a story."""
        story = await self.get_by_id(user_id, story_id)
        await self.repository.delete(story)
