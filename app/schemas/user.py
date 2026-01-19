"""User Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str | None = None


class UserUpdate(BaseModel):
    """Schema for updating user data."""

    email: EmailStr | None = None
    password: str | None = Field(
        default=None, min_length=8, description="Password must be at least 8 characters"
    )
    full_name: str | None = None
    is_active: bool | None = None


class UserAdminUpdate(UserUpdate):
    """Schema for admin updating user data (includes admin flag)."""

    is_admin: bool | None = None


class UserResponse(BaseModel):
    """Schema for user response data (public, no password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserInDB(UserBase):
    """Schema for user data from database (internal use)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
