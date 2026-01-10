from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy.orm import Session, selectinload, joinedload

from core.constants import check_the_cart, calculate_total_price, check_product_quantity
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
def add_to_cart(order: OrderItemCreate, cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == order.product_id).scalar()
    if not product:
        raise HTTPException(status_code=404, detail='No product found.')

    db_order = db.query(OrderItem).filter(OrderItem.cart_id == cart.id, OrderItem.product_id == product.id).first()

    if db_order:
        if product.stock_quantity < db_order.quantity:
            raise HTTPException(status_code=400, detail='Quantity is already taken.')
        db_order.quantity += order.quantity
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        cart.total_price = calculate_total_price(db, cart)

        db.add(cart)
        db.commit()
        return db_order

    new_order_item = OrderItem(**order.model_dump(),price_at_purchase=product.price ,cart_id = cart.id)

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    cart.total_price = calculate_total_price(db, cart)

    db.add(cart)
    db.commit()

    return new_order_item

@router.put("/item/{item_id}", response_model=CartResponse)
def change_order_quantity(item_id: int, quantity: int, cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):

    cart_item = db.query(OrderItem).filter(OrderItem.cart_id == cart.id, OrderItem.id == item_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail='OrderItem not found.')

    if check_product_quantity(cart_item.product_id, cart_item, db):
        raise HTTPException(status_code=400, detail='Quantity is already taken.')

    cart_item.quantity += quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    cart.total_price = calculate_total_price(db, cart)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    return cart

@router.delete("/item/{item_id}")
def delete_item_from_cart(item_id: int, cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):
    cart_item = db.query(OrderItem).filter(OrderItem.id == item_id).scalar()
    if not cart_item:
        raise HTTPException(status_code=404, detail='OrderItem not found.')
    cart.total_price -= abs(cart_item.price_at_purchase * cart_item.quantity)
    db.delete(cart_item)
    db.commit()
    return f"Item {item_id} was successfully deleted."

@router.delete("/")
def clear_cart(cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):
    cart.total_price = 0
    for item in cart.items:
        db.delete(item)
    db.commit()
    return "Cart was successfully cleared."