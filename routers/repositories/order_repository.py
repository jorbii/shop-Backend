from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from db.models import Order, OrderItem, UserAddress, Product
from db.enums import OrderStatus
from .base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository для роботи з замовленнями"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Отримати замовлення за ID з усіма елементами"""
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).joinedload(OrderItem.product))
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[Order]:
        """Отримати всі замовлення користувача"""
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items).joinedload(OrderItem.product))
        )
        return result.scalars().all()
    
    async def get_cart_items(self, cart_id: int) -> List[OrderItem]:
        """Отримати всі елементи кошика, які ще не в замовленні"""
        result = await self.db.execute(
            select(OrderItem).where(
                OrderItem.cart_id == cart_id,
                OrderItem.order_id.is_(None)
            )
        )
        return result.scalars().all()
    
    async def create(
        self,
        user_id: int,
        cart_id: int,
        address_id: int,
        total_price: float
    ) -> Order:
        """Створити нове замовлення"""
        order = Order(
            user_id=user_id,
            cart_id=cart_id,
            address_id=address_id,
            status=OrderStatus.NEW,
            total_price=total_price
        )
        self.db.add(order)
        await self.db.flush()
        return order
    
    async def update_status(self, order: Order, status: OrderStatus) -> Order:
        """Оновити статус замовлення"""
        order.status = status
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def link_items_to_order(self, order_id: int, items: List[OrderItem]) -> None:
        """Прив'язати елементи до замовлення"""
        for item in items:
            item.order_id = order_id
            self.db.add(item)
        await self.db.flush()
