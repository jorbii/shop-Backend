from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from db.enums import *
from db.models import OrderItem, Cart, User, Order
from db.database import get_db
from routers.auth import get_current_user

router = APIRouter()

@router.get("/utils/enums")
def get_enums():
    return {
        "order_status": [e.value for e in OrderStatus],
        "payment_status": [e.value for e in PaymentStatus],
        "payment_type": [e.value for e in PaymentType]
    }

def calculate_total_price(cart_id: int, db: Session = Depends(get_db)):
    items = db.query(OrderItem).filter(OrderItem.cart_id == cart_id).all()

    total_price_sum = sum(item.quantity * item.price_at_purchase for item in items)

    return total_price_sum

def check_the_cart(current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    try:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).scalar()
        return cart

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "The cart is empty."})

def order_status(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order).get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} is already cancelled"
        )

    return order
