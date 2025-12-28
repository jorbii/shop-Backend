from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy.orm import Session, selectinload, joinedload

from core.constants import calculate_total_price, check_the_cart
from db.database import get_db
from db.models import User, OrderItem, Cart, Product
from db.shemas import OrderItemResponse, OrderItemCreate, CartResponse
from routers.auth import get_current_user


router = APIRouter()

@router.get('/', response_model=CartResponse)
def get_cart(current_user: User = Depends(get_current_user), db =  Depends(get_db)):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .options(
            selectinload(Cart.items).options(
                joinedload(OrderItem.product).options(
                    joinedload(Product.category)
                )
            )
        )
        .first()
    )

    if not cart:
        raise HTTPException(status_code=404, detail='No cart found.')

    return cart

@router.post('/item', response_model=OrderItemResponse)
def add_to_cart(order: OrderItemCreate, cart: Cart = Depends(check_the_cart), current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):

    db_order = db.query(OrderItem).filter(OrderItem.cart_id == cart.id, Cart.user_id == current_user.id).scalar()
    if db_order:
        db_order.quantity += order.quantity
        db_order.total_price = calculate_total_price(cart.id, db)
        db.commit()
        db.refresh(db_order)
        return db_order

    new_order_item = OrderItem(**order.model_dump(), cart_id = cart.id)

    db.add(new_order_item)
    db.commit()
    db.flush()


    product = db.query(Product).filter(Product.id == new_order_item.product_id).scalar()

    new_order_item.price_at_purchase = product.price

    cart.total_price = calculate_total_price(cart.id)

    db.add(new_order_item)
    db.add(cart)
    db.commit()

    return new_order_item


@router.put("/item/{item_id}", response_model=CartResponse)
def change_order_quantity(item_id: int, quantity: int, cart: Cart = Depends(check_the_cart), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    cart_item = db.query(OrderItem).filter(OrderItem.cart_id == cart.id, OrderItem.id == item_id).scalar()

    if not cart_item:
        raise HTTPException(status_code=404, detail='OrderItem not found.')

    cart_item.quantity += quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart)

    return cart

@router.delete("/item/{item_id}")
def delete_item_from_cart(item_id: int, cart: Cart = Depends(check_the_cart), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(OrderItem).filter(OrderItem.id == item_id).scalar()
    if not cart_item:
        raise HTTPException(status_code=404, detail='OrderItem not found.')
    cart.total_price -= abs(cart_item.price_at_purchase)
    db.delete(cart_item)
    db.commit()
    return f"Item {item_id} was successfully deleted."

@router.delete("/")
def clear_cart(cart: Cart = Depends(check_the_cart), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart.total_price = 0
    db.delete(cart)
    db.commit()
    return "Cart was successfully cleared."