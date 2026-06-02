from app.exceptions.app_exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


class ProductService:

    def __init__(self, repository: ProductRepository):
        self._repo = repository

    async def create_product(self, data: ProductCreate, seller_id: int) -> ProductResponse:
        existing = await self._repo.get_by_sku(data.sku)
        if existing:
            raise ConflictException(f"A product with SKU '{data.sku}' already exists.")
        product = await self._repo.create({**data.model_dump(), "user_id": seller_id})
        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: int) -> ProductResponse:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return ProductResponse.model_validate(product)

    async def get_all_products(self) -> list[ProductResponse]:
        products = await self._repo.get_all()
        return [ProductResponse.model_validate(p) for p in products]

    async def get_seller_products(self, seller_id: int) -> list[ProductResponse]:
        """Reuses get_by_seller repo helper — seller sees only their own products."""
        products = await self._repo.get_by_seller(seller_id)
        return [ProductResponse.model_validate(p) for p in products]

    async def update_product(self, product_id: int, data: ProductUpdate, seller_id: int | None = None) -> ProductResponse:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)

        # If seller_id provided, ensure they own this product
        if seller_id and product.user_id != seller_id:
            from app.exceptions.app_exceptions import ForbiddenException
            raise ForbiddenException("You can only edit your own products.")

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise BadRequestException("No fields provided for update.")

        if "sku" in update_data and update_data["sku"] != product.sku:
            existing = await self._repo.get_by_sku(update_data["sku"])
            if existing:
                raise ConflictException(f"A product with SKU '{update_data['sku']}' already exists.")

        updated = await self._repo.update(product_id, update_data)
        return ProductResponse.model_validate(updated)

    async def delete_product(self, product_id: int, seller_id: int | None = None) -> None:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)

        if seller_id and product.user_id != seller_id:
            from app.exceptions.app_exceptions import ForbiddenException
            raise ForbiddenException("You can only delete your own products.")

        await self._repo.delete(product_id)

    async def get_raw_product(self, product_id: int) -> Product:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return product
