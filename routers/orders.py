from fastapi import HTTPException, APIRouter, Depends,status

from sqlalchemy.orm import Session

from core.constants import calculate_total_price
from db.database import get_db
from db.enums import OrderStatus
from db.models import User, Order, UserAddress, Cart
from db.shemas import OrderResponse, OrderCreate
from routers.auth import get_current_user


router = APIRouter()

@router.post('/', response_model=OrderResponse)
def create_order(address: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).scalar()

    if not cart:
        raise HTTPException(status_code=401, detail="Login please")

    cart_items = [item for item in cart.items if item.order_id is None] if cart else []
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    address_id = None

    if address.address_id:
        db_address = db.query(UserAddress).filter(UserAddress.id == address.id,
                                              UserAddress.user_id == current_user.id).scalar()
        if not db_address:
            raise HTTPException(
                status_code=404,
                detail="Inputted address is not found",
            )

        address_id = db_address.id

    else:
        new_address = UserAddress(user_id = current_user.id, **address.model_dump(exclude={'address_id'}))

        address_id = new_address.id

        db.add(new_address)
        db.commit()
        db.flush()

    order = Order(user_id=current_user.id, status=OrderStatus.NEW, cart_id=cart.id, address_id = address_id)

    try:
        db.add(order)
        db.commit()
        db.flush()

        order.total_price = calculate_total_price(order.id)

        return order

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/{order_id}', response_model=OrderResponse)
def order_info(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@router.delete('/{order_id}')
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return "Order canceled successfully"









