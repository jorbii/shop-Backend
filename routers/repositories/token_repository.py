from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import TokenBlackList
from .base_repository import BaseRepository


class TokenRepository(BaseRepository[TokenBlackList]):
    """Repository для роботи з чорним списком токенів"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(TokenBlackList, db)
    
    async def is_blacklisted(self, token: str) -> bool:
        """Перевірити чи токен в чорному списку"""
        result = await self.db.execute(
            select(TokenBlackList).where(TokenBlackList.token == token)
        )
        return result.scalar_one_or_none() is not None
    
    async def add_to_blacklist(self, token: str) -> TokenBlackList:
        """Додати токен до чорного списку"""
        blacklisted_token = TokenBlackList(token=token)
        self.db.add(blacklisted_token)
        await self.db.flush()
        await self.db.refresh(blacklisted_token)
        return blacklisted_token
