from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import ComparisonProducts
from .base_repository import BaseRepository


class ComparisonRepository(BaseRepository[ComparisonProducts]):
    """Repository для роботи з таблицею порівняння продуктів"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ComparisonProducts, db)
    
    async def get_by_user_id(self, user_id: int) -> List[ComparisonProducts]:
        """Отримати всі продукти для порівняння користувача"""
        result = await self.db.execute(
            select(ComparisonProducts).where(ComparisonProducts.user_id == user_id)
        )
        return result.scalars().all()
    
    async def create(self, user_id: int, product_id: int) -> ComparisonProducts:
        """Додати продукт до таблиці порівняння"""
        comparison = ComparisonProducts(
            user_id=user_id,
            product_id=product_id
        )
        self.db.add(comparison)
        await self.db.flush()
        await self.db.refresh(comparison)
        return comparison
