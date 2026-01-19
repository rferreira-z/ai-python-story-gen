"""Authentication service for business logic."""

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Token


class AuthService:
    """Service for Authentication business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user with email and password."""
        user = await self.repository.get_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens for a user."""
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh an access token using a refresh token."""
        payload = decode_token(refresh_token)
        if payload is None:
            raise UnauthorizedError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise BadRequestError("Invalid token type")

        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid refresh token")

        user = await self.repository.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedError("User not found")

        if not user.is_active:
            raise UnauthorizedError("User is inactive")

        return self.create_tokens(user)
