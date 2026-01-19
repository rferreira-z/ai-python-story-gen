"""Pydantic schemas for Story."""

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
