from app.models.user import UserRole
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.dashboard import DashboardStats
from app.schemas.product import ProductResponse

LOW_STOCK_THRESHOLD = 10


class DashboardService:
    """
    Reuses count_by_role from UserRepository instead of a separate CustomerRepository.
    No duplicate query logic.
    """

    def __init__(
        self,
        product_repo: ProductRepository,
        user_repo: UserRepository,
        order_repo: OrderRepository,
    ):
        self._product_repo = product_repo
        self._user_repo = user_repo
        self._order_repo = order_repo

    async def get_stats(self) -> DashboardStats:
        total_products = await self._product_repo.count()
        total_customers = await self._user_repo.count_by_role(UserRole.CUSTOMER)
        total_sellers = await self._user_repo.count_by_role(UserRole.SELLER)
        total_orders = await self._order_repo.count()
        low_stock = await self._product_repo.get_low_stock(threshold=LOW_STOCK_THRESHOLD)

        return DashboardStats(
            total_products=total_products,
            total_customers=total_customers,
            total_sellers=total_sellers,
            total_orders=total_orders,
            low_stock_products=[ProductResponse.model_validate(p) for p in low_stock],
        )
