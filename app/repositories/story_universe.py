"""StoryUniverse repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story_universe import StoryUniverse


class StoryUniverseRepository:
    """Repository for StoryUniverse database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, universe_id: int) -> StoryUniverse | None:
        """Get a story universe by ID."""
        result = await self.session.execute(
            select(StoryUniverse).where(StoryUniverse.id == universe_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_id(
        self, user_id: int, universe_id: int
    ) -> StoryUniverse | None:
        """Get a story universe by user ID and universe ID."""
        result = await self.session.execute(
            select(StoryUniverse).where(
                StoryUniverse.id == universe_id, StoryUniverse.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[StoryUniverse]:
        """Get all story universes for a user with pagination."""
        result = await self.session.execute(
            select(StoryUniverse)
            .where(StoryUniverse.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, universe: StoryUniverse) -> StoryUniverse:
        """Create a new story universe."""
        self.session.add(universe)
        await self.session.flush()
        await self.session.refresh(universe)
        return universe

    async def update(
        self, universe: StoryUniverse, update_data: dict
    ) -> StoryUniverse:
        """Update a story universe with the given data."""
        for field, value in update_data.items():
            if value is not None:
                setattr(universe, field, value)
        await self.session.flush()
        await self.session.refresh(universe)
        return universe

    async def delete(self, universe: StoryUniverse) -> None:
        """Delete a story universe."""
        await self.session.delete(universe)
        await self.session.flush()
