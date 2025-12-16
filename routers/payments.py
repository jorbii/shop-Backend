from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from typing import List
from db.database import get_db
from db.enums import PaymentStatus, PaymentType
from db.models import User, CreditCard, Payment, Order
from db.shemas import PaymentResponse, PaymentCreate, WriteCreditCard
from .auth import get_current_user
router = APIRouter()

@router.post("/initiate")
def create_payment(payment: PaymentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(
        Order.id == payment.order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found or access denied")

    if payment.payment_type == PaymentType.CREDIT_CARD:
        if payment.credit_card is None:
            raise HTTPException(status_code=400, detail="Credit card is required")

        payment_data = db.query(Payment).join(Order).options(
            selectinload(Payment.order)
        ).filter(
            Order.id == payment.order_id
        ).first()

        # if payment_data:
        #     amount = payment_data.total_price
        # else:
        #     raise HTTPException(status_code=400, detail="Order haven`t been found")

        transaction = Payment(
            user_id=current_user.id,
            order_id=payment.order_id,
            payment_type=PaymentType.CREDIT_CARD
        )

        db.add(transaction)

        if payment.save_card:
            save_credit_card = CreditCard(
                user_id=current_user.id,
                cart_number=payment.credit_card.card_number,
                create_date=payment.credit_card.create_date,
                ccv=payment.credit_card.ccv,
                holder_name=payment.credit_card.holder_name
            )

            db.add(save_credit_card)

        db.commit()
        return {"status": "paid", "receipt": transaction.id}
    return {"msg": "Other methods not implemented yet"}




    # db_payment = CreditCart(
    #     user_id=current_user.id,
    #     **payment.model_dump()
    # )
    #
    # if not db_payment:
    #     raise HTTPException(status_code=404, detail="Payment haven't been created")
    #
    # db.add(db_payment)
    # db.commit()
    #
    # return db_payment
