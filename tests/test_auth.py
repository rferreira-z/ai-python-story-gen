"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Test successful user registration."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    """Test registration with duplicate email fails."""
    # First registration
    await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    # Second registration with same email
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(async_client: AsyncClient):
    """Test registration with invalid email fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "invalidemail",
            "password": "password123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(async_client: AsyncClient):
    """Test registration with short password fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    """Test successful login."""
    # First register a user
    await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "logintest@example.com",
            "password": "password123",
        },
    )

    # Then login
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={
            "username": "logintest@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient):
    """Test login with wrong password fails."""
    # First register a user
    await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpassword123",
        },
    )

    # Then login with wrong password
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    """Test login with non-existent user fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(async_client: AsyncClient):
    """Test successful token refresh."""
    # First register and login
    await async_client.post(
        f"{settings.api_v1_prefix}/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "password123",
        },
    )
    login_response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/login",
        data={
            "username": "refresh@example.com",
            "password": "password123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Then refresh
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client: AsyncClient):
    """Test refresh with invalid token fails."""
    response = await async_client.post(
        f"{settings.api_v1_prefix}/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
