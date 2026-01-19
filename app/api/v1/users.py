"""User CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    get_current_active_user,
    get_current_admin_user,
    get_user_service,
)
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update current authenticated user's profile."""
    # Prevent users from updating is_active through this endpoint
    update_data = user_in.model_dump(exclude_unset=True)
    update_data.pop("is_active", None)  # Remove is_active if present
    user_update = UserUpdate.model_validate(update_data)

    user = await user_service.update_user(current_user.id, user_update)
    return UserResponse.model_validate(user)


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: Annotated[User, Depends(get_current_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[UserResponse]:
    """List all users (admin only)."""
    users = await user_service.get_all(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    _: Annotated[User, Depends(get_current_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Get a user by ID (admin only)."""
    user = await user_service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserAdminUpdate,
    _: Annotated[User, Depends(get_current_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update a user by ID (admin only)."""
    user = await user_service.update_user_admin(user_id, user_in)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    _: Annotated[User, Depends(get_current_admin_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Delete a user by ID (admin only)."""
    await user_service.delete_user(user_id)
