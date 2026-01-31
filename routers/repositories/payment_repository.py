from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Payment, CreditCard
from db.enums import PaymentStatus
from .base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository для роботи з платежами"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)
    
    async def create(
        self,
        user_id: int,
        order_id: int,
        credit_card_id: Optional[int] = None,
        status: PaymentStatus = PaymentStatus.PENDING
    ) -> Payment:
        """Створити новий платіж"""
        payment = Payment(
            user_id=user_id,
            order_id=order_id,
            credit_card_id=credit_card_id,
            status=status
        )
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment


class CreditCardRepository(BaseRepository[CreditCard]):
    """Repository для роботи з кредитними картками"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(CreditCard, db)
    
    async def find_by_last_4_numbers(self, user_id: int, last_4_numbers: str) -> Optional[CreditCard]:
        """Знайти картку за останніми 4 цифрами"""
        result = await self.db.execute(
            select(CreditCard).where(
                CreditCard.user_id == user_id,
                CreditCard.last_4_numbers == last_4_numbers
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_id: int, last_4_numbers: str) -> CreditCard:
        """Створити нову картку"""
        card = CreditCard(
            user_id=user_id,
            last_4_numbers=last_4_numbers
        )
        self.db.add(card)
        await self.db.flush()
        await self.db.refresh(card)
        return card
