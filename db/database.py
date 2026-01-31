# db/async_session.py
from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import settings

# Асинхронний engine
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True, future=True)

# Асинхронна сесія
AsyncSessionLocal = sessionmaker( expire_on_commit=False, bind=engine, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
# Dependency для FastAPI
async def get_async_db() -> AsyncGenerator[Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session
