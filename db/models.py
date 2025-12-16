from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import String, ForeignKey, Integer, DECIMAL, Boolean, Text, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from db.enums import OrderStatus, PaymentStatus, PaymentType, HolderName  # Припускаємо, що це імпортовано коректно


# --- МОДЕЛІ (Таблиці) ---

class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    addresses: Mapped[List["UserAddress"]] = relationship(back_populates="country")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(200))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Виправлено назву relationship на orders, щоб відповідало логіці
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    addresses: Mapped[List["UserAddress"]] = relationship(back_populates="user")
    payments: Mapped[List["Payment"]] = relationship(back_populates="user")

    # Додано для зручності доступу до порівнянь
    comparisons: Mapped[List["ComparisonProducts"]] = relationship(back_populates="user")


class UserAddress(Base):
    __tablename__ = "addresses"

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


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2))
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String)

    category: Mapped["Category"] = relationship(back_populates="products")
    reviews: Mapped[List["Review"]] = relationship(
        back_populates="product")  # Виправлено back_populates на однину ("product"), див. клас Review
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")

    # ✅ ВИПРАВЛЕННЯ: Додано відсутній атрибут
    comparison_products: Mapped[List["ComparisonProducts"]] = relationship(back_populates="product")


class ComparisonProducts(Base):
    __tablename__ = "comparison_products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Product"] = relationship(back_populates="comparison_products")
    # Додаємо зв'язок з юзером (опціонально, але корисно)
    user: Mapped["User"] = relationship(back_populates="comparisons")


# ✅ ВИПРАВЛЕННЯ: Перейменовано клас Cart -> Order та таблицю "cart" -> "orders"
# Це важливо, бо OrderItem та Payment посилаються на "orders.id"
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.NEW)
    total_price: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="orders")  # змінено cart -> orders
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[Optional["Payment"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))  # Тепер це посилання коректне
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price_at_purchase: Mapped[float] = mapped_column(DECIMAL(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class CreditCard(Base):
    __tablename__ = "creditcard"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # provider: Mapped[str] = mapped_column(String(50))
    # token: Mapped[str] = mapped_column(String(255))
    cart_number: Mapped[str] = mapped_column(String(50))
    create_date: Mapped[date] = mapped_column(Date)
    ccv: Mapped[str] = mapped_column(String(4))
    holder_name: Mapped[HolderName] = mapped_column()

    payments: Mapped[list["Payment"]] = relationship(back_populates="credit_card")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    credit_card_id: Mapped[int | None] = mapped_column(ForeignKey("creditcard.id"), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    payment_type: Mapped[PaymentType] = mapped_column(default=PaymentType.CREDIT_CARD)

    credit_card: Mapped["CreditCard"] = relationship(back_populates="payments")
    order: Mapped["Order"] = relationship(back_populates="payments")
    user: Mapped["User"] = relationship(back_populates="payments")

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")