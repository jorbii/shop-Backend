from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer

from db.enums import PaymentType
from db.models import OrderStatus


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
    login: str = Field(min_length=4, max_length=64)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    phone_number: Optional[str] = None


# Створення (реєстрація) - тут потрібен пароль
class UserCreate(UserBase):
    email: EmailStr = Field(min_length=2, max_length=50)
    password: str = Field(min_length=3, max_length=72, description="Пароль мінімум 8 символів")

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

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

class WriteToken(UserBase):
    sub: str
    exp: Decimal
    token_type: str


# ==========================================
# 3. АДРЕСИ (ADDRESSES)
# ==========================================

class AddressBase(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    city: str
    street: str
    postal_code: str
    is_default: bool = False


class OrderCreate(AddressBase):
    address_id: int | None


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
    price: Decimal
    category_id: int
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    stock_quantity: int = Field(ge=0, default=0)


# Для оновлення (всі поля опціональні)
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = 0
    stock_quantity: Optional[int] = 0
    category_id: Optional[int] = 0


class ProductResponse(ProductBase):
    id: int
    stock_quantity: int
    category: Optional[CategoryResponse] = None

    @field_serializer('price')
    def serialize_price(self, price: Decimal, _info):
        # Перетворюємо на float для JSON
        return float(price)

    class Config:
        from_attributes = True

class ComparisonProductsResponse(BaseModel):
    user_id: int
    product_id: int

    product: ProductResponse

# ==========================================
# 5. ЗАМОВЛЕННЯ (ORDERS) - Найскладніше
# ==========================================

# Елемент замовлення (при створенні ми знаємо тільки ID товару і кількість)
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

# Елемент замовлення (при перегляді ми хочемо бачити деталі товару)
class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    price_at_purchase: Decimal

    # Або вкласти повний об'єкт товару (скорочений)
    product: Optional[ProductResponse] = None

    @field_serializer('price_at_purchase')
    def serialize_price(self, price: Decimal, _info):
        return float(price)

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    user_id: int
    status: OrderStatus  # Використовуємо Enum
    total_price: Decimal
    created_at: datetime
    payment_type: str
    items: List[OrderItemResponse]

    @field_serializer('total_price')
    def serialize_price(self, price: Decimal, _info):
        return float(price)

    class Config:
        from_attributes = True



class CartResponse(BaseModel):
    user_id: int
    total_price: Decimal

    items: List[OrderItemResponse]

    @field_serializer("total_price")
    def serialize_price(self, price: Decimal, _info):
        return float(price)

    class Config:
        from_attributes = True


# ==========================================
# 6. ВІДГУКИ (REVIEWS)
# ==========================================

class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)  # 1-5 зірок
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    user_id: int
    user_name: str  # Припустимо, ми додамо @property в модель User або через join
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 7. ПЛАТЕЖІ (PAYMENTS)
# ==========================================

class WriteCreditCard(BaseModel):
    card_number: str
    create_date: date
    ccv: str
    holder_name: str

    @field_serializer('card_number')
    def serialize_cart_number(self, cart_number: str, _info):
        if not cart_number.isdigit() or len(cart_number) != 16:
            raise ValueError('Unexpected cart number')
        return cart_number

class CreditCardResponse(WriteCreditCard):
    id: int

class PaymentCreate(BaseModel):
    payment_type: PaymentType
    credit_card: Optional[WriteCreditCard] = None
    save_card: bool = False

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    order_id: int
    total_price: Decimal
    status: str
    payment_type: PaymentType
    created_at: datetime

    @field_serializer('total_price')
    def serialize_price(self, price: Decimal, _info):
        # Перетворюємо на float для JSON
        return float(price)

    class Config:
        from_attributes = True

