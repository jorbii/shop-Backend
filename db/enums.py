import enum

class OrderStatus(enum.Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class PaymentType(enum.Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    GOOGLE_PAY = "google_pay"
    APPLE_PAY = "apple_pay"
    CASH_ON_DELIVERY = "cash_on_delivery"
    BANK_TRANSFER = "bank_transfer"