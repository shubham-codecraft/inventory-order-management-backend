from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.order import OrderStatus
from app.schemas.product import ProductResponse


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product: ProductResponse

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(..., min_length=1)
    # user_id is injected from the authenticated customer — not sent in body


class OrderResponse(BaseModel):
    id: int
    user_id: int  # customer reference
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    order_items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
