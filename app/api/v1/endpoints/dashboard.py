from fastapi import APIRouter, Depends

from app.core.dependencies import get_dashboard_service, require_admin
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get dashboard stats (Admin only)",
)
async def get_dashboard_stats(
    service: DashboardService = Depends(get_dashboard_service),
    _: User = Depends(require_admin),
):
    return await service.get_stats()
