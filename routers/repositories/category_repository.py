from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Category
from .base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository для роботи з категоріями"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Отримати категорію за ID"""
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Category]:
        """Отримати всі категорії"""
        result = await self.db.execute(select(Category))
        return result.scalars().all()
    
    async def create(self, **kwargs) -> Category:
        """Створити нову категорію"""
        category = Category(**kwargs)
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def update(self, category_id: int, **kwargs) -> Optional[Category]:
        """Оновити категорію"""
        category = await self.get_by_id(category_id)
        if not category:
            return None
        
        for key, value in kwargs.items():
            setattr(category, key, value)
        
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def delete(self, category_id: int) -> bool:
        """Видалити категорію"""
        category = await self.get_by_id(category_id)
        if not category:
            return False
        
        await self.db.delete(category)
        await self.db.flush()
        return True
