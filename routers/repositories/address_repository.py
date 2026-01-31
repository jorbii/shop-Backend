from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import UserAddress
from .base_repository import BaseRepository


class AddressRepository(BaseRepository[UserAddress]):
    """Repository для роботи з адресами користувачів"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserAddress, db)
    
    async def get_by_id(self, address_id: int) -> Optional[UserAddress]:
        """Отримати адресу за ID"""
        result = await self.db.execute(select(UserAddress).where(UserAddress.id == address_id))
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> List[UserAddress]:
        """Отримати всі адреси користувача"""
        result = await self.db.execute(
            select(UserAddress).where(UserAddress.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_user_address(self, address_id: int, user_id: int) -> Optional[UserAddress]:
        """Отримати адресу користувача за ID адреси та ID користувача"""
        result = await self.db.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, **kwargs) -> UserAddress:
        """Створити нову адресу"""
        address = UserAddress(**kwargs)
        self.db.add(address)
        await self.db.flush()
        await self.db.refresh(address)
        return address
