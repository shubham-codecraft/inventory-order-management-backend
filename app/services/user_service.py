from app.exceptions.app_exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse, UserUpdate


class UserService:
    """
    Admin-only service for managing users.
    Reuses shared UserRepository helpers for both seller and customer operations
    — no duplicate query logic.

    """

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def get_all_sellers(self) -> list[UserResponse]:
        users = await self._repo.get_by_role(UserRole.SELLER)
        return [UserResponse.model_validate(u) for u in users]

    async def get_all_customers(self) -> list[UserResponse]:
        users = await self._repo.get_by_role(UserRole.CUSTOMER)
        return [UserResponse.model_validate(u) for u in users]


    async def get_by_id(self, user_id: int) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> UserResponse:
        user = await self._repo.get_by_email(email)
        if not user:
            raise NotFoundException("User", email)
        return UserResponse.model_validate(user)

    async def update(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            from app.exceptions.app_exceptions import BadRequestException
            raise BadRequestException("No fields provided for update.")

        # Prevent email collision
        if "email" in update_data and update_data["email"] != user.email:
            existing = await self._repo.get_by_email(update_data["email"])
            if existing:
                raise ConflictException(f"Email '{update_data['email']}' is already taken.")

        updated = await self._repo.update(user_id, update_data)
        return UserResponse.model_validate(updated)

    async def delete(self, user_id: int) -> None:
        deleted = await self._repo.delete(user_id)
        if not deleted:
            raise NotFoundException("User", user_id)

    async def toggle_active(self, user_id: int) -> UserResponse:
        """Enable or disable a user account."""
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        updated = await self._repo.update(user_id, {"is_active": not user.is_active})
        return UserResponse.model_validate(updated)
