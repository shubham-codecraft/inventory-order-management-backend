from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_order_service, require_admin, require_customer
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderResponse, OrderSummary
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Place an order (Customer / Admin)")
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_customer),
):
    # customer user_id injected from token
    return await service.create_order(payload, customer_user_id=current_user.id)


@router.get("/", response_model=list[OrderSummary], summary="List all orders (Admin only)")
async def list_orders(
    service: OrderService = Depends(get_order_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_orders()


@router.get("/mine", response_model=list[OrderSummary], summary="Get my orders (Customer)")
async def my_orders(
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_customer),
):
    return await service.get_my_orders(current_user.id)


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order details")
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_customer),
):
    customer_id = None if current_user.role == UserRole.ADMIN else current_user.id
    return await service.get_order(order_id, customer_user_id=customer_id)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancel an order")
async def cancel_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_customer),
):
    customer_id = None if current_user.role == UserRole.ADMIN else current_user.id
    await service.cancel_order(order_id, customer_user_id=customer_id)
