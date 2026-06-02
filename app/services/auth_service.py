from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.app_exceptions import BadRequestException, UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    """Single Responsibility: authentication only. No customer table dependency."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self._user_repo.get_by_email(data.email)
        if existing:
            raise BadRequestException(f"Email '{data.email}' is already registered.")

        user = await self._user_repo.create({
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "full_name": data.full_name,
            "phone_number": data.phone_number,
            "role": data.role,
            "is_active": True,
        })
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Contact support.")

        token = create_access_token(
            subject=user.id,
            extra_claims={"role": user.role.value},
        )
        return TokenResponse(access_token=token, role=user.role)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found.")
        return UserResponse.model_validate(user)
