from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User, OrderItem
from db.shemas import OrderItemResponse, OrderItemCreate
from routers.auth import get_current_user


router = APIRouter()

@router.post('/', response_model=OrderItemResponse)
def add_to_cart(order: OrderItemCreate, current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    if order.button_name == "add_to_cart":
        db_order = db.query(OrderItem).filter(OrderItem.order_id == order.order_id).scalar()
        if db_order:
            raise HTTPException(status_code=400, detail='Order already added to cart.')

        new_order_item = OrderItem(**order.model_dump(exclude={'button_name'}))

        db.add(new_order_item)
        db.commit()

        return "The product have benn added to cart."
    # elif order.button_name == "buy_in_one_click":



