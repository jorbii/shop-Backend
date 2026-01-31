from typing import List
from fastapi import HTTPException, APIRouter, Depends, status
from db.shemas import UserUpdate, UserResponse, OrderResponse
from routers.routes.auth import get_current_user
from routers.repositories.dependencies import (
    get_user_repository,
    get_order_repository
)
from routers.repositories import UserRepository, OrderRepository
from db.models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def user_info(current_user: User = Depends(get_current_user)):
    """Отримати інформацію про поточного користувача"""
    return current_user


@router.put('/me', response_model=UserResponse)
async def change_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Оновити інформацію про користувача"""
    # Перевірка на дублікати email/login
    check_user = await user_repo.check_email_or_login_exists(
        email=user_update.email if user_update.email and user_update.email != current_user.email else None,
        login=user_update.login if user_update.login and user_update.login != current_user.login else None
    )
    
    if check_user:
        if user_update.email and check_user.email == user_update.email:
            raise HTTPException(status_code=400, detail=f"Email {user_update.email} already exists")
        if user_update.login and check_user.login == user_update.login:
            raise HTTPException(status_code=400, detail=f"Login {user_update.login} already exists")

    # Оновлення даних
    updated_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
    updated_user = await user_repo.update(current_user, **updated_data)
    await user_repo.db.commit()
    await user_repo.db.refresh(updated_user)
    
    return updated_user


@router.delete('/me')
async def delete_user(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Видалити користувача"""
    if current_user:
        await user_repo.delete(current_user)
        await user_repo.db.commit()
        return f"User with id = {current_user.id} have been successfully deleted"
    return None


@router.get('/orders', response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    order_repo: OrderRepository = Depends(get_order_repository)
):
    """Отримати всі замовлення користувача"""
    db_orders = await order_repo.get_by_user_id(current_user.id)
    return db_orders or []
