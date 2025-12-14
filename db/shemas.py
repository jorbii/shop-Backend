from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, PositiveFloat

from db.models import OrderStatus, PaymentType, PaymentStatus


# ==========================================
# 1. ЗАГАЛЬНІ ТА ДОПОМІЖНІ СХЕМИ
# ==========================================

class CountryResponse(BaseModel):
    code: str
    name: str
    currency_code: str
    tax_rate: float

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. КОРИСТУВАЧ (USER)
# ==========================================

# Базова схема (спільні поля)
class UserBase(BaseModel):
    login: str = Field(min_length=8, max_length=64)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: Optional[str] = None


# Створення (реєстрація) - тут потрібен пароль
class UserCreate(UserBase):
    email: EmailStr = Field(min_length=2, max_length=50)
    password: str = Field(min_length=3, max_length=72, description="Пароль мінімум 8 символів")

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    login: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]

# Логін
class UserLogin(BaseModel):
    login: str = Field(min_length=1, max_length=70)
    password: str = Field(min_length=3, max_length=72)

class UserForgotPassword(UserBase):
    email: EmailStr = Field(min_length=2, max_length=50)

class UserChangePassword(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. АДРЕСИ (ADDRESSES)
# ==========================================

class AddressBase(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    city: str
    street: str
    postal_code: str
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    # Можемо вкласти назву країни
    country: Optional[CountryResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. ТОВАРИ ТА КАТЕГОРІЇ (PRODUCTS)
# ==========================================

class CategoryBase(BaseModel):
    name: str
    # parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: PositiveFloat
    category_id: int
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    stock_quantity: int = Field(ge=0, default=0)


# Для оновлення (всі поля опціональні)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    stock_quantity: int
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 5. ЗАМОВЛЕННЯ (ORDERS) - Найскладніше
# ==========================================

# Елемент замовлення (при створенні ми знаємо тільки ID товару і кількість)
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


# Створення замовлення (список товарів)
class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    # Адресу можна передати ID або об'єктом, для спрощення візьмемо ID
    address_id: int
    payment_method_id: Optional[int] = None  # Якщо платимо збереженою карткою


# Елемент замовлення (при перегляді ми хочемо бачити деталі товару)
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str  # Можна витягнути з product.name через ORM
    quantity: int
    price_at_purchase: Decimal  # Історична ціна

    # Або вкласти повний об'єкт товару (скорочений)
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus  # Використовуємо Enum
    total_price: Decimal
    created_at: datetime
    items: List[OrderItemResponse]  # Вкладений список товарів

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 6. ВІДГУКИ (REVIEWS)
# ==========================================

class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)  # 1-5 зірок
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str  # Припустимо, ми додамо @property в модель User або через join
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 7. ПЛАТЕЖІ (PAYMENTS)
# ==========================================

class PaymentCreate(BaseModel):
    order_id: int
    amount: Decimal
    payment_type: PaymentType
    # token передається, якщо це нова карта
    token: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    amount: Decimal
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)