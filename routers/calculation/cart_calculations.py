from fastapi import Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import get_async_db
from db.models import OrderItem, Cart, User
from routers.routes.auth import get_current_user


async def calculate_total_price(db: AsyncSession, cart: Cart) -> float:
    """Розраховує загальну ціну кошика"""
    try:
        stmt = select(func.sum(OrderItem.quantity * OrderItem.price_at_purchase)).where(
            OrderItem.cart_id == cart.id
        )
        result = await db.execute(stmt)
        total_price = result.scalar_one_or_none()

        return total_price or 0.0
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The cart is empty.")


async def check_the_cart(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
) -> Cart:
    """Перевіряє та повертає кошик користувача"""
    try:
        stmt = select(Cart).where(Cart.user_id == current_user.id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The cart is empty."
            )
        return cart
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The cart is empty."
        )
