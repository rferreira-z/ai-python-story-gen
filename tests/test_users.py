"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.models.user import User


@pytest.mark.asyncio
async def test_get_current_user(async_client: AsyncClient, test_user: User, user_token: str):
    """Test getting current user profile."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(async_client: AsyncClient):
    """Test getting current user without auth fails."""
    response = await async_client.get(f"{settings.api_v1_prefix}/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_current_user(async_client: AsyncClient, test_user: User, user_token: str):
    """Test updating current user profile."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_list_users_admin(
    async_client: AsyncClient, test_admin_user: User, admin_token: str
):
    """Test admin can list all users."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_users_non_admin_forbidden(
    async_client: AsyncClient, test_user: User, user_token: str
):
    """Test non-admin cannot list all users."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id_admin(
    async_client: AsyncClient, test_user: User, test_admin_user: User, admin_token: str
):
    """Test admin can get user by ID."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_user_by_id_non_admin_forbidden(
    async_client: AsyncClient, test_user: User, test_admin_user: User, user_token: str
):
    """Test non-admin cannot get user by ID."""
    response = await async_client.get(
        f"{settings.api_v1_prefix}/users/{test_admin_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_admin(
    async_client: AsyncClient, test_user: User, test_admin_user: User, admin_token: str
):
    """Test admin can update user."""
    response = await async_client.put(
        f"{settings.api_v1_prefix}/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"full_name": "Admin Updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Admin Updated"


@pytest.mark.asyncio
async def test_delete_user_admin(
    async_client: AsyncClient, test_admin_user: User, admin_token: str
):
    """Test admin can delete user."""
    # First create a user to delete
    register_response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "todelete@example.com",
            "password": "password123",
        },
    )
    user_id = register_response.json()["id"]

    # Then delete
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_non_admin_forbidden(
    async_client: AsyncClient, test_user: User, test_admin_user: User, user_token: str
):
    """Test non-admin cannot delete user."""
    response = await async_client.delete(
        f"{settings.api_v1_prefix}/users/{test_admin_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check endpoint."""
    response = await async_client.get(f"{settings.api_v1_prefix}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
