"""User service for business logic."""

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserAdminUpdate, UserCreate, UserUpdate


class UserService:
    """Service for User business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_by_id(self, user_id: int) -> User:
        """Get a user by ID, raises NotFoundError if not found."""
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User with id {user_id} not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        return await self.repository.get_by_email(email)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user, raises ConflictError if email exists."""
        existing_user = await self.repository.get_by_email(user_in.email)
        if existing_user:
            raise ConflictError(f"User with email {user_in.email} already exists")

        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
        )
        return await self.repository.create(user)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """Update a user."""
        user = await self.get_by_id(user_id)

        update_data = user_in.model_dump(exclude_unset=True)

        # Check for email conflict if email is being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await self.repository.get_by_email(update_data["email"])
            if existing_user:
                raise ConflictError(f"User with email {update_data['email']} already exists")

        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return await self.repository.update(user, update_data)

    async def update_user_admin(self, user_id: int, user_in: UserAdminUpdate) -> User:
        """Update a user (admin version with more fields)."""
        user = await self.get_by_id(user_id)

        update_data = user_in.model_dump(exclude_unset=True)

        # Check for email conflict if email is being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await self.repository.get_by_email(update_data["email"])
            if existing_user:
                raise ConflictError(f"User with email {update_data['email']} already exists")

        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return await self.repository.update(user, update_data)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        await self.repository.delete(user)
