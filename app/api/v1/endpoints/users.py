from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_user_service, require_admin
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/sellers", response_model=list[UserResponse], summary="List all sellers (Admin)")
async def list_sellers(
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_sellers()


@router.get("/customers", response_model=list[UserResponse], summary="List all customers (Admin)")
async def list_customers(
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_customers()


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID (Admin)")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    return await service.get_by_id(user_id)


@router.put("/{user_id}", response_model=UserResponse, summary="Update user (Admin)")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    return await service.update(user_id, payload)


@router.patch("/{user_id}/toggle-active", response_model=UserResponse, summary="Enable/disable user (Admin)")
async def toggle_active(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    return await service.toggle_active(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (Admin)")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_admin),
):
    await service.delete(user_id)
