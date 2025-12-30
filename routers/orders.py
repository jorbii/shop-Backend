from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy.orm import Session

from core.constants import order_status, check_the_cart
from db.database import get_db
from db.enums import OrderStatus
from db.models import User, Order, UserAddress, Cart
from db.shemas import OrderResponse, OrderCreate


router = APIRouter()

@router.post('/', response_model=OrderResponse)
def create_order(address: OrderCreate, cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):
    cart_items = [item for item in cart.items if item.order_id is None] if cart else []

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    if address.address_id:
        db_address = db.query(UserAddress).filter(UserAddress.id == address.address_id,
                                              UserAddress.user_id == cart.user_id).scalar()
        if not db_address:
            raise HTTPException(
                status_code=404,
                detail="Inputted address is not found"
            )

        address_id = db_address.id

    else:
        new_address = UserAddress(user_id = cart.user_id, **address.model_dump(exclude={'address_id'}))

        db.add(new_address)
        db.commit()
        db.flush()

        address_id = new_address.id

    order = Order(user_id=cart.user_id, status=OrderStatus.NEW, total_price=cart.total_price ,cart_id=cart.id, address_id = address_id)

    try:
        db.add(order)
        db.commit()
        db.flush()

        for item in cart_items:
            item.order_id = order.id

        db.commit()
        db.refresh(order)

        return order

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/{order_id}', response_model=OrderResponse)
def order_info(order: Order = Depends(order_status), db: Session = Depends(get_db)):
    order = order
    return order


@router.patch('/{order_id}')
def delete_order(
        order: Order = Depends(order_status),
        db: Session = Depends(get_db)
):

    order.status = OrderStatus.CANCELLED

    db.commit()

    return {"message": "Order canceled successfully"}