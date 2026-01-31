from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from db.models import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository для роботи з користувачами"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Отримати користувача за ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_login(self, login: str) -> Optional[User]:
        """Отримати користувача за логіном"""
        result = await self.db.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Отримати користувача за email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def check_email_or_login_exists(self, email: str = None, login: str = None) -> Optional[User]:
        """Перевірити чи існує користувач з таким email або login"""
        conditions = []
        if email:
            conditions.append(User.email == email)
        if login:
            conditions.append(User.login == login)
        
        if not conditions:
            return None
        
        result = await self.db.execute(select(User).where(or_(*conditions)))
        return result.scalar_one_or_none()
    
    async def create(self, **kwargs) -> User:
        """Створити нового користувача"""
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User, **kwargs) -> User:
        """Оновити користувача"""
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        """Видалити користувача"""
        await self.db.delete(user)
        await self.db.flush()
