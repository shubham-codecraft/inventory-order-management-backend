from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.base import AbstractRepository


class ProductRepository(AbstractRepository[Product]):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: int) -> Product | None:
        result = await self._session.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Product | None:
        result = await self._session.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Product]:
        result = await self._session.execute(select(Product).order_by(Product.id))
        return list(result.scalars().all())

    async def get_by_seller(self, user_id: int) -> list[Product]:
        """Returns all products belonging to a specific seller."""
        result = await self._session.execute(
            select(Product).where(Product.user_id == user_id).order_by(Product.id)
        )
        return list(result.scalars().all())

    async def get_low_stock(self, threshold: int = 10) -> list[Product]:
        result = await self._session.execute(
            select(Product)
            .where(Product.quantity_in_stock <= threshold)
            .order_by(Product.quantity_in_stock)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> Product:
        product = Product(**data)
        self._session.add(product)
        await self._session.flush()
        await self._session.refresh(product)
        return product

    async def update(self, id: int, data: dict) -> Product | None:
        await self._session.execute(
            update(Product).where(Product.id == id).values(**data)
        )
        await self._session.flush()
        return await self.get_by_id(id)

    async def decrement_stock(self, product_id: int, quantity: int) -> None:
        await self._session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(quantity_in_stock=Product.quantity_in_stock - quantity)
        )
        await self._session.flush()

    async def restore_stock(self, product_id: int, quantity: int) -> None:
        await self._session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(quantity_in_stock=Product.quantity_in_stock + quantity)
        )
        await self._session.flush()

    async def delete(self, id: int) -> bool:
        product = await self.get_by_id(id)
        if not product:
            return False
        await self._session.delete(product)
        await self._session.flush()
        return True

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Product))
        return result.scalar_one()
