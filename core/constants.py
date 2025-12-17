from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.enums import *
from db.models import OrderItem
from db.database import get_db

router = APIRouter()

@router.get("/utils/enums")
def get_enums():
    return {
        "order_status": [e.value for e in OrderStatus],
        "payment_status": [e.value for e in PaymentStatus],
        "payment_type": [e.value for e in PaymentType]
    }

def calculate_total_price(order_id: int, db: Session = Depends(get_db)):
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    total_price_sum = sum(item.quantity * item.price_at_purchase for item in items)

    return total_price_sum | 0

