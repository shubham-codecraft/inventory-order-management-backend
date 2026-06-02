from decimal import Decimal

from app.exceptions.app_exceptions import BadRequestException, InsufficientStockException, NotFoundException
from app.models.order import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderSummary


class OrderService:
    """
    Single Responsibility: order business logic.
    Depends on UserRepository (DIP) instead of removed CustomerRepository.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        user_repo: UserRepository,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._user_repo = user_repo

    async def create_order(self, data: OrderCreate, customer_user_id: int) -> OrderResponse:
        # 1. Validate customer exists
        customer = await self._user_repo.get_by_id(customer_user_id)
        if not customer:
            raise NotFoundException("User", customer_user_id)

        # 2. Validate all products and stock — validate everything before any mutation
        validated_items: list[tuple] = []
        for item in data.items:
            product = await self._product_repo.get_by_id(item.product_id)
            if not product:
                raise NotFoundException("Product", item.product_id)
            if product.quantity_in_stock < item.quantity:
                raise InsufficientStockException(
                    product_name=product.name,
                    available=product.quantity_in_stock,
                    requested=item.quantity,
                )
            validated_items.append((product, item.quantity))

        # 3. Calculate total (backend always owns this)
        total_amount = sum(
            Decimal(str(p.price)) * qty for p, qty in validated_items
        )

        # 4. Create order
        order = await self._order_repo.create({
            "user_id": customer_user_id,
            "status": OrderStatus.CONFIRMED,
            "total_amount": total_amount,
        })

        # 5. Create items + decrement stock atomically
        for product, quantity in validated_items:
            await self._order_repo.add_order_item(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
            )
            await self._product_repo.decrement_stock(product.id, quantity)

        full_order = await self._order_repo.get_by_id(order.id)
        return OrderResponse.model_validate(full_order)

    async def get_order(self, order_id: int, customer_user_id: int | None = None) -> OrderResponse:
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        # If customer_user_id provided, ensure they own this order
        if customer_user_id and order.user_id != customer_user_id:
            from app.exceptions.app_exceptions import ForbiddenException
            raise ForbiddenException("You can only view your own orders.")
        return OrderResponse.model_validate(order)

    async def get_all_orders(self) -> list[OrderSummary]:
        orders = await self._order_repo.get_all()
        return [OrderSummary.model_validate(o) for o in orders]

    async def get_my_orders(self, customer_user_id: int) -> list[OrderSummary]:
        """Customer-specific view — reuses get_by_user repo helper."""
        orders = await self._order_repo.get_by_user(customer_user_id)
        return [OrderSummary.model_validate(o) for o in orders]

    async def cancel_order(self, order_id: int, customer_user_id: int | None = None) -> None:
        order = await self._order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)
        if customer_user_id and order.user_id != customer_user_id:
            from app.exceptions.app_exceptions import ForbiddenException
            raise ForbiddenException("You can only cancel your own orders.")
        if order.status == OrderStatus.CANCELLED:
            raise BadRequestException(f"Order {order_id} is already cancelled.")

        for item in order.order_items:
            await self._product_repo.restore_stock(item.product_id, item.quantity)

        await self._order_repo.update_status(order_id, OrderStatus.CANCELLED)
