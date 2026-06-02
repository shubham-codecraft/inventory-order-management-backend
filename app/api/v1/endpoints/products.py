from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user, get_product_service, require_seller
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse], summary="List all products (public)")
async def list_products(service: ProductService = Depends(get_product_service)):
    return await service.get_all_products()


@router.get("/mine", response_model=list[ProductResponse], summary="Get seller's own products")
async def my_products(
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(require_seller),
):
    return await service.get_seller_products(current_user.id)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get a product (public)")
async def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return await service.get_product(product_id)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Create product (Seller / Admin)")
async def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(require_seller),
):
    # seller_id injected from token — not trusted from request body
    return await service.create_product(payload, seller_id=current_user.id)


@router.put("/{product_id}", response_model=ProductResponse, summary="Update product (Seller / Admin)")
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(require_seller),
):
    seller_id = None if current_user.role.value == "admin" else current_user.id
    return await service.update_product(product_id, payload, seller_id=seller_id)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete product (Seller / Admin)")
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
    current_user: User = Depends(require_seller),
):
    seller_id = None if current_user.role.value == "admin" else current_user.id
    await service.delete_product(product_id, seller_id=seller_id)
