"""Authentication Pydantic schemas."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str | None = None
    exp: int | None = None
    type: str | None = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str
