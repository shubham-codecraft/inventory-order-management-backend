from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.base import AbstractRepository


class OrderRepository(AbstractRepository[Order]):

    def __init__(self, session: AsyncSession):
        self._session = session

    def _with_relations(self):
        """Shared eager-load option — reused by get_by_id and get_all."""
        return (
            select(Order)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product),
                selectinload(Order.customer),
            )
        )

    async def get_by_id(self, id: int) -> Order | None:
        result = await self._session.execute(
            self._with_relations().where(Order.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Order]:
        result = await self._session.execute(
            self._with_relations().order_by(Order.id.desc())
        )
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[Order]:
        """Returns all orders placed by a specific customer."""
        result = await self._session.execute(
            self._with_relations()
            .where(Order.user_id == user_id)
            .order_by(Order.id.desc())
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def add_order_item(self, order_id: int, product_id: int, quantity: int, unit_price) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self._session.add(item)
        await self._session.flush()
        return item

    async def update_status(self, order_id: int, status: OrderStatus) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.status = status
        await self._session.flush()
        return order

    async def delete(self, id: int) -> bool:
        order = await self.get_by_id(id)
        if not order:
            return False
        await self._session.delete(order)
        await self._session.flush()
        return True

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(Order))
        return result.scalar_one()
