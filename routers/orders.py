from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from typing import List

from core.constants import calculate_total_price
from db.database import get_db
from db.enums import OrderStatus
from db.models import User, Order, UserAddress, OrderItem
from db.shemas import OrderResponse
from routers.auth import get_current_user


router = APIRouter()

@router.post('/', response_model=OrderResponse)
def add_to_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = Order(user_id = current_user.id, status = OrderStatus.NEW)

    db.add(order)
    db.commit()
    db.refresh(order)

    address_id = db.query(UserAddress).options(selectinload(UserAddress.orders)).filter(UserAddress.orders.id == order.id).scalar()

    order.address_id = address_id.id
    order.total_price = calculate_total_price(order.id)

    db.commit()

    return order








