"""Dependency functions для отримання repository instances"""
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from fastapi import Depends

from .product_repository import ProductRepository
from .user_repository import UserRepository
from .cart_repository import CartRepository
from .order_repository import OrderRepository
from .order_item_repository import OrderItemRepository
from .payment_repository import PaymentRepository, CreditCardRepository
from .comparison_repository import ComparisonRepository
from .category_repository import CategoryRepository
from .address_repository import AddressRepository
from .token_repository import TokenRepository


def get_product_repository(db: AsyncSession = Depends(get_async_db)) -> ProductRepository:
    """Отримати ProductRepository"""
    return ProductRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    """Отримати UserRepository"""
    return UserRepository(db)


def get_cart_repository(db: AsyncSession = Depends(get_async_db)) -> CartRepository:
    """Отримати CartRepository"""
    return CartRepository(db)


def get_order_repository(db: AsyncSession = Depends(get_async_db)) -> OrderRepository:
    """Отримати OrderRepository"""
    return OrderRepository(db)


def get_order_item_repository(db: AsyncSession = Depends(get_async_db)) -> OrderItemRepository:
    """Отримати OrderItemRepository"""
    return OrderItemRepository(db)


def get_payment_repository(db: AsyncSession = Depends(get_async_db)) -> PaymentRepository:
    """Отримати PaymentRepository"""
    return PaymentRepository(db)


def get_credit_card_repository(db: AsyncSession = Depends(get_async_db)) -> CreditCardRepository:
    """Отримати CreditCardRepository"""
    return CreditCardRepository(db)


def get_comparison_repository(db: AsyncSession = Depends(get_async_db)) -> ComparisonRepository:
    """Отримати ComparisonRepository"""
    return ComparisonRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_async_db)) -> CategoryRepository:
    """Отримати CategoryRepository"""
    return CategoryRepository(db)


def get_address_repository(db: AsyncSession = Depends(get_async_db)) -> AddressRepository:
    """Отримати AddressRepository"""
    return AddressRepository(db)


def get_token_repository(db: AsyncSession = Depends(get_async_db)) -> TokenRepository:
    """Отримати TokenRepository"""
    return TokenRepository(db)
