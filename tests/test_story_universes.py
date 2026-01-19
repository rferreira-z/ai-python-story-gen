"""Tests for story universe endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.story_universe import StoryUniverse
from app.models.user import User


@pytest.fixture
async def test_universe(test_session: AsyncSession, test_user: User) -> StoryUniverse:
    """Create a test story universe."""
    universe = StoryUniverse(
        user_id=test_user.id,
        name="Test Universe",
        description="A test universe description in markdown.",
    )
    test_session.add(universe)
    await test_session.commit()
    await test_session.refresh(universe)
    return universe


@pytest.mark.asyncio
async def test_create_story_universe(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test creating a story universe."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/story-universes",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "My Universe", "description": "# My Universe\n\nA detailed world."},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Universe"
    assert data["description"] == "# My Universe\n\nA detailed world."
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_story_universe_minimal(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test creating a story universe with only required fields."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/story-universes",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Minimal Universe"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Universe"
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_story_universe_empty_name_fails(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test creating a story universe with empty name fails validation."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/story-universes",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": ""},
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_story_universe_unauthorized(async_client: AsyncClient):
    """Test creating a story universe without auth fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/story-universes",
        json={"name": "Unauthorized Universe"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_story_universes(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test listing story universes for current user."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(u["id"] == test_universe.id for u in data)


@pytest.mark.asyncio
async def test_list_story_universes_empty(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test listing story universes when none exist."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_story_universes_pagination(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test pagination on story universes list."""
    # Create multiple universes
    for i in range(5):
        await async_client.post(
            f"{settings.api_v1_prefix}/story-universes",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": f"Universe {i}"},
        )

    # Test pagination
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes?skip=2&limit=2",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_story_universe(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test getting a story universe by ID."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes/{test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_universe.id
    assert data["name"] == test_universe.name
    assert data["description"] == test_universe.description


@pytest.mark.asyncio
async def test_get_story_universe_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test getting a non-existent story universe."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_other_user_universe_not_found(
    async_client: AsyncClient,
    test_session: AsyncSession,
    test_user: User,
    test_admin_user: User,
    user_token: str,
):
    """Test that a user cannot access another user's universe."""
    # Create universe for admin user
    other_universe = StoryUniverse(
        user_id=test_admin_user.id,
        name="Admin Universe",
        description="Admin's universe",
    )
    test_session.add(other_universe)
    await test_session.commit()
    await test_session.refresh(other_universe)

    # Try to access as regular user
    response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes/{other_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_story_universe(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test updating a story universe."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/story-universes/{test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Updated Universe", "description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Universe"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_story_universe_partial(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test partial update of a story universe."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/story-universes/{test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"description": "Only description updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_universe.name  # Unchanged
    assert data["description"] == "Only description updated"


@pytest.mark.asyncio
async def test_update_story_universe_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test updating a non-existent story universe."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/story-universes/99999",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Updated"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story_universe(
    async_client: AsyncClient,
    test_user: User,
    user_token: str,
    test_universe: StoryUniverse,
):
    """Test deleting a story universe."""
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/story-universes/{test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await async_client.get(
        f"{settings.api_v1_prefix}/story-universes/{test_universe.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_story_universe_not_found(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test deleting a non-existent story universe."""
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/story-universes/99999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
