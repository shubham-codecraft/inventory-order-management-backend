from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.database import get_db
from app.exceptions.app_exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User, UserRole
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.order_service import OrderService
from app.services.product_service import ProductService
from app.services.user_service import UserService

_bearer = HTTPBearer()

# ---------------------------------------------------------------------------
# Repository providers
# ---------------------------------------------------------------------------

def get_product_repository(session: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(session)

def get_order_repository(session: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(session)

def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)

# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------

def get_product_service(
    repo: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    return ProductService(repo)

def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> OrderService:
    return OrderService(order_repo, product_repo, user_repo)

def get_dashboard_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    order_repo: OrderRepository = Depends(get_order_repository),
) -> DashboardService:
    return DashboardService(product_repo, user_repo, order_repo)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)

# ---------------------------------------------------------------------------
# Auth guards
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: int = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise UnauthorizedException("Invalid or expired token.")
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")
    return user

def require_role(*roles: UserRole):
    """Factory for role guards — avoids duplicating guard logic per role."""
    async def guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Requires role: {', '.join(r.value for r in roles)}."
            )
        return current_user
    return guard

# Convenience shortcuts
require_admin    = require_role(UserRole.ADMIN)
require_seller   = require_role(UserRole.SELLER, UserRole.ADMIN)
require_customer = require_role(UserRole.CUSTOMER, UserRole.ADMIN)
