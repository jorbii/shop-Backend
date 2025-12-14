from datetime import datetime
from typing import List, Optional
import enum
from uuid import uuid4
from db.database import Base
from sqlalchemy import String, ForeignKey, Integer, DECIMAL, Boolean, Text, DateTime, Date, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from db.enums import *

# --- МОДЕЛІ (Таблиці) ---

class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)  # ISO код: 'UA', 'US'
    name: Mapped[str] = mapped_column(String(100))

    # Зв'язок: Країна має багато адрес доставки
    addresses: Mapped[List["UserAddress"]] = relationship(back_populates="country")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(200))# Пароль має бути захешований!
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Зв'язки
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    addresses: Mapped[List["UserAddress"]] = relationship(back_populates="user")
    payment_methods: Mapped[List["PaymentMethod"]] = relationship(back_populates="user")


class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    country_code: Mapped[str] = mapped_column(ForeignKey("countries.code"))
    city: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(200))
    postal_code: Mapped[str] = mapped_column(String(20))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="addresses")
    country: Mapped["Country"] = relationship(back_populates="addresses")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))

    products: Mapped[List["Product"]] = relationship(back_populates="category")
    #
    # children: Mapped[List["Category"]] = relationship("Category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))  # DECIMAL важливий для грошей!
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String)

    category: Mapped["Category"] = relationship(back_populates="products")
    reviews: Mapped[List["Review"]] = relationship(back_populates="product")
    # Цей зв'язок потрібен, щоб бачити, в яких замовленнях фігурував товар
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.NEW)
    total_price: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payment: Mapped[Optional["Payment"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    # Фіксуємо ціну на момент покупки!
    price_at_purchase: Mapped[float] = mapped_column(DECIMAL(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[str] = mapped_column(String(50))  # 'stripe', 'liqpay'
    token: Mapped[str] = mapped_column(String(255))  # Токен, а не номер карти!
    last_4_digits: Mapped[str] = mapped_column(String(4))

    user: Mapped["User"] = relationship(back_populates="payment_methods")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2))
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))  # ID від банку

    order: Mapped["Order"] = relationship(back_populates="payment")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")