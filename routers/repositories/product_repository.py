from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from db.models import Product
from .base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository для роботи з продуктами"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Отримати продукт за ID"""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Product]:
        """Отримати всі продукти"""
        result = await self.db.execute(select(Product))
        return result.scalars().all()
    
    async def search(self, query: str) -> List[Product]:
        """Пошук продуктів за назвою або описом"""
        if not query:
            return []
        
        result = await self.db.execute(
            select(Product).where(
                or_(
                    Product.name.contains(query.lower()),
                    Product.description.contains(query.lower())
                )
            )
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> Product:
        """Створити новий продукт"""
        product = Product(**kwargs)
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def update(self, product_id: int, **kwargs) -> Optional[Product]:
        """Оновити продукт"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        for key, value in kwargs.items():
            setattr(product, key, value)
        
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Видалити продукт"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.delete(product)
        await self.db.flush()
        return True
    
    async def decrease_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """Зменшити кількість товару на складі"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        product.stock_quantity -= quantity
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
