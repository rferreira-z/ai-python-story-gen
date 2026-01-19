"""Story repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import Story


class StoryRepository:
    """Repository for Story database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, story_id: int) -> Story | None:
        """Get a story by ID."""
        result = await self.session.execute(
            select(Story).where(Story.id == story_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_id(self, user_id: int, story_id: int) -> Story | None:
        """Get a story by user ID and story ID."""
        result = await self.session.execute(
            select(Story).where(Story.id == story_id, Story.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Story]:
        """Get all stories for a user with pagination."""
        result = await self.session.execute(
            select(Story).where(Story.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_by_universe(
        self, user_id: int, universe_id: int, skip: int = 0, limit: int = 100
    ) -> list[Story]:
        """Get all stories in a universe for a user with pagination."""
        result = await self.session.execute(
            select(Story)
            .where(Story.user_id == user_id, Story.story_universe_id == universe_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, story: Story) -> Story:
        """Create a new story."""
        self.session.add(story)
        await self.session.flush()
        await self.session.refresh(story)
        return story

    async def update(self, story: Story, update_data: dict) -> Story:
        """Update a story with the given data."""
        for field, value in update_data.items():
            if value is not None:
                setattr(story, field, value)
        await self.session.flush()
        await self.session.refresh(story)
        return story

    async def delete(self, story: Story) -> None:
        """Delete a story."""
        await self.session.delete(story)
        await self.session.flush()
