import enum

class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class PaymentType(enum.Enum):
    credit_card = "credit_card"
    paypal = "paypal"
    google_pay = "google_pay"
    apple_pay = "apple_pay"
    cash_on_delivery = "cash_on_delivery"
    bank_transfer = "bank_transfer"

class HolderName(enum.Enum):
    visa = "visa"
    mastercard = "mastercard"
