from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, selectinload

from db.database import get_db
from db.enums import *
from db.models import OrderItem, Cart, User, Order, Product
from routers.auth import get_current_user

router = APIRouter()

@router.get("/utils/enums")
def get_enums():
    return {
        "order_status": [e.value for e in OrderStatus],
        "payment_status": [e.value for e in PaymentStatus],
        "payment_type": [e.value for e in PaymentType]
    }

def calculate_total_price(db, cart):
    try:
        total_price = db.query(func.sum(OrderItem.quantity * OrderItem.price_at_purchase)) \
            .filter(OrderItem.cart_id == cart.id).scalar()
        return total_price
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The cart is empty.")

def check_the_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
        return cart

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "The cart is empty."})

def order_status(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.query(Order) \
        .filter(Order.id == order_id) \
        .options(selectinload(Order.items).joinedload(OrderItem.product)) \
        .scalar()

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


def check_product_quantity(product_id, order_item, db):
    product = db.query(Product).get(product_id)

    if product.stock_quantity >= order_item.quantity:
        product.stock_quantity -= order_item.quantity
        db.add(product)
        db.commit()
        return False
    else:
        return True