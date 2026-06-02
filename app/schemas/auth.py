from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str | None = None
    role: UserRole = UserRole.CUSTOMER

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Admin-only user update schema."""
    full_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    role: UserRole | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: str | None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
