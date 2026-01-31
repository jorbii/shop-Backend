from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import OrderItem
from .base_repository import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository для роботи з елементами замовлення"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OrderItem, db)
    
    async def get_by_id(self, item_id: int) -> Optional[OrderItem]:
        """Отримати елемент за ID"""
        result = await self.db.execute(select(OrderItem).where(OrderItem.id == item_id))
        return result.scalar_one_or_none()
    
    async def get_by_cart_and_product(self, cart_id: int, product_id: int) -> Optional[OrderItem]:
        """Отримати елемент кошика для конкретного продукту"""
        result = await self.db.execute(
            select(OrderItem).where(
                OrderItem.cart_id == cart_id,
                OrderItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
        price_at_purchase: float
    ) -> OrderItem:
        """Створити новий елемент кошика"""
        item = OrderItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            price_at_purchase=price_at_purchase
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def add_quantity(self, item: OrderItem, quantity: int) -> OrderItem:
        """Додати кількість до існуючого елемента"""
        item.quantity += quantity
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item: OrderItem) -> None:
        """Видалити елемент"""
        await self.db.delete(item)
        await self.db.flush()
