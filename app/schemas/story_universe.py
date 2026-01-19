"""Pydantic schemas for StoryUniverse."""

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
