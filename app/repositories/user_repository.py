from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base import AbstractRepository


class UserRepository(AbstractRepository[User]):
    """
    Single repository for all User DB operations.
    Shared helpers (get_by_role, count_by_role, update) are reused
    by UserService for both seller and customer operations — no duplication.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # AbstractRepository contract
    # ------------------------------------------------------------------

    async def get_by_id(self, id: int) -> User | None:
        result = await self._session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def create(self, data: dict) -> User:
        user = User(**data)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, id: int) -> bool:
        user = await self.get_by_id(id)
        if not user:
            return False
        await self._session.delete(user)
        await self._session.flush()
        return True

    # ------------------------------------------------------------------
    # Shared helpers — reused by UserService for seller + customer ops
    # ------------------------------------------------------------------

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole) -> list[User]:
        """Returns all users with a given role. Reused for get_all_sellers / get_all_customers."""
        result = await self._session.execute(
            select(User).where(User.role == role).order_by(User.id)
        )
        return list(result.scalars().all())

    async def get_by_id_and_role(self, id: int, role: UserRole) -> User | None:
        """Fetch a user only if they have the expected role — avoids role confusion."""
        result = await self._session.execute(
            select(User).where(User.id == id, User.role == role)
        )
        return result.scalar_one_or_none()

    async def update(self, id: int, data: dict) -> User | None:
        """Generic update — reused for both seller and customer updates by UserService."""
        await self._session.execute(
            update(User).where(User.id == id).values(**data)
        )
        await self._session.flush()
        return await self.get_by_id(id)

    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role — reused by DashboardService."""
        result = await self._session.execute(
            select(func.count()).select_from(User).where(User.role == role)
        )
        return result.scalar_one()
