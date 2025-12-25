from typing import List

from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from db.database import get_db
from db.models import User, Order, Cart, OrderItem
from db.shemas import UserUpdate, UserResponse, OrderResponse
from routers.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put('/me', response_model=UserResponse)
def change_user(
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    check_list = []
    if user_update.email and user_update.email != current_user.email:
        check_list.append(User.email == user_update.email)
    if user_update.login and user_update.login != current_user.login:
        check_list.append(User.login == user_update.login)

    if check_list:
        check_user = db.query(User).filter(or_(*check_list)).first()

        if check_user:
            if user_update.email and check_user.email == user_update.email:
                raise HTTPException(status_code=400, detail=f"Email {user_update.email} already exists")
            if user_update.login and check_user.login == user_update.login:
                raise HTTPException(status_code=400, detail=f"Login {user_update.login} already exists")

    # 4. Оновлення полів
    updated_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in updated_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete('/me')
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user:
        db.delete(current_user)
        db.commit()
        return f"User with id = {current_user.id} have been successfully deleted"
    return None



@router.get('/orders', response_model=List[OrderResponse])
def get_orders(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_orders = db.query(Order) \
        .filter(Order.user_id == current_user.id) \
        .options(selectinload(Order.items).joinedload(OrderItem.product)) \
        .all()

    if db_orders is None:
        return db_orders

    return []

