from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from db.database import get_async_db
from db.enums import OrderStatus
from db.models import Order, OrderItem


def get_order_status_dependency(order_id: int):
    """Factory function для створення dependency для перевірки статусу замовлення"""
    async def order_status(
        db: AsyncSession = Depends(get_async_db)
    ) -> Order:
        """Перевіряє статус замовлення та повертає його"""
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).joinedload(OrderItem.product))
        )

        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order {order_id} is already cancelled"
            )

        return order
    
    return order_status


async def order_status(
    order_id: int,
    db: AsyncSession = Depends(get_async_db)
) -> Order:
    """Перевіряє статус замовлення та повертає його"""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).joinedload(OrderItem.product))
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} is already cancelled"
        )

    return order
