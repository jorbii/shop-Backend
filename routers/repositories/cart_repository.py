from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from db.models import Cart, OrderItem, Product
from .base_repository import BaseRepository


class CartRepository(BaseRepository[Cart]):
    """Repository для роботи з кошиками"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Cart, db)
    
    async def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        """Отримати кошик користувача з усіма елементами"""
        result = await self.db.execute(
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).options(
                    joinedload(OrderItem.product).options(
                        joinedload(Product.category)
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: int) -> Cart:
        """Створити новий кошик для користувача"""
        cart = Cart(user_id=user_id, total_price=0)
        self.db.add(cart)
        await self.db.flush()
        await self.db.refresh(cart)
        return cart
    
    async def update_total_price(self, cart: Cart, total_price: float) -> Cart:
        """Оновити загальну ціну кошика"""
        cart.total_price = total_price
        self.db.add(cart)
        await self.db.flush()
        await self.db.refresh(cart)
        return cart
    
    async def clear_cart(self, cart: Cart) -> Cart:
        """Очистити кошик (видалити всі елементи)"""
        cart.total_price = 0
        for item in cart.items:
            await self.db.delete(item)
        await self.db.flush()
        return cart
