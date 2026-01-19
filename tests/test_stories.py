"""Tests for story endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.story import Story
from app.models.story_universe import StoryUniverse
from app.models.user import User


@pytest.fixture
async def test_universe(test_session: AsyncSession, test_user: User) -> StoryUniverse:
    """Create a test story universe."""
    universe = StoryUniverse(
        user_id=test_user.id,
        name="Test Universe",
        description="A test universe for stories.",
    )
    test_session.add(universe)
    await test_session.commit()
    await test_session.refresh(universe)
    return universe


@pytest.fixture
async def test_story(
    test_session: AsyncSession, test_user: User, test_universe: StoryUniverse
) -> Story:
    """Create a test story."""
    story = Story(
        user_id=test_user.id,
        story_universe_id=test_universe.id,
        title="Test Story",
        content="# Chapter 1\n\nOnce upon a time...",
        image_urls=None,  # SQLite doesn't support ARRAY, so use None for tests
    )
    test_session.add(story)
    await test_session.commit()
    await test_session.refresh(story)
    return story


@pytest.mark.asyncio
async def test_create_story(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test creating a story."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "story_universe_id": test_universe.id,
            "title": "My First Story",
            "content": "This is the story content.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Story"
    assert data["content"] == "This is the story content."
    assert data["story_universe_id"] == test_universe.id
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_story_minimal(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test creating a story with only required fields."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "story_universe_id": test_universe.id,
            "title": "Minimal Story",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Story"
    assert data["content"] is None


@pytest.mark.asyncio
async def test_create_story_empty_title_fails(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test creating a story with empty title fails validation."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "story_universe_id": test_universe.id,
            "title": "",
        },
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_story_invalid_universe(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test creating a story in a non-existent universe fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "story_universe_id": 99999,
            "title": "Story in Invalid Universe",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_story_other_user_universe(
    async_client: AsyncClient,
    test_session: AsyncSession,
    test_user: User,
    test_admin_user: User,
    user_token: str,
):
    """Test creating a story in another user's universe fails."""
    # Create universe for admin
    admin_universe = StoryUniverse(
        user_id=test_admin_user.id,
        name="Admin Universe",
        description="Admin's universe",
    )
    test_session.add(admin_universe)
    await test_session.commit()
    await test_session.refresh(admin_universe)

    # Try to create story in admin's universe as regular user
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "story_universe_id": admin_universe.id,
            "title": "Unauthorized Story",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_story_unauthorized(
    async_client: AsyncClient, test_universe: StoryUniverse
):
    """Test creating a story without auth fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/stories",
        json={
            "story_universe_id": test_universe.id,
            "title": "Unauthorized Story",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_stories(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
):
    """Test listing all stories for current user."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["id"] == test_story.id for s in data)


@pytest.mark.asyncio
async def test_list_stories_by_universe(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
    test_universe: StoryUniverse,
):
    """Test listing stories filtered by universe."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories?universe_id={test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # All returned stories should be in the specified universe
    for story in data:
        assert story["story_universe_id"] == test_universe.id


@pytest.mark.asyncio
async def test_list_stories_by_invalid_universe(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test listing stories with invalid universe_id."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories?universe_id=99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_stories_empty(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test listing stories when none exist."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_stories_pagination(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test pagination on stories list."""
    # Create multiple stories
    for i in range(5):
        await async_client.post(
            f"{settings.api_v1_prefix}/stories",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "story_universe_id": test_universe.id,
                "title": f"Story {i}",
            },
        )

    # Test pagination
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories?skip=2&limit=2",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_story(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
):
    """Test getting a story by ID."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories/{test_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_story.id
    assert data["title"] == test_story.title
    assert data["content"] == test_story.content


@pytest.mark.asyncio
async def test_get_story_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test getting a non-existent story."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_other_user_story_not_found(
    async_client: AsyncClient,
    test_session: AsyncSession,
    test_user: User,
    test_admin_user: User,
    user_token: str,
):
    """Test that a user cannot access another user's story."""
    # Create universe and story for admin
    admin_universe = StoryUniverse(
        user_id=test_admin_user.id,
        name="Admin Universe",
        description="Admin's universe",
    )
    test_session.add(admin_universe)
    await test_session.commit()
    await test_session.refresh(admin_universe)

    admin_story = Story(
        user_id=test_admin_user.id,
        story_universe_id=admin_universe.id,
        title="Admin Story",
        content="Admin's story content",
        image_urls=None,
    )
    test_session.add(admin_story)
    await test_session.commit()
    await test_session.refresh(admin_story)

    # Try to access as regular user
    response = await async_client.get(
        f"{settings.api_v1_prefix}/stories/{admin_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_story(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
):
    """Test updating a story."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/stories/{test_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Updated Story", "content": "Updated content"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Story"
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_update_story_partial(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
):
    """Test partial update of a story."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/stories/{test_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"content": "Only content updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_story.title  # Unchanged
    assert data["content"] == "Only content updated"


@pytest.mark.asyncio
async def test_update_story_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test updating a non-existent story."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/stories/99999",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Updated"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_story: Story,
):
    """Test deleting a story."""
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/stories/{test_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await async_client.get(
        f"{settings.api_v1_prefix}/stories/{test_story.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test deleting a non-existent story."""
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/stories/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
