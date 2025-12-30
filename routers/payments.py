from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session

from core.constants import order_status
from db.database import get_db
from db.enums import PaymentStatus, PaymentType
from db.models import User, CreditCard, Payment, Order
from db.shemas import PaymentCreate
from .auth import get_current_user

router = APIRouter()

@router.post("/initiate")
def create_payment(payment: PaymentCreate, order: Order = Depends(order_status) ,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    if order:
        amount = order.total_price
    else:
        raise HTTPException(status_code=400, detail="Order haven`t been found")

    if payment.payment_type == PaymentType.credit_card:
        if payment.credit_card is None:
            raise HTTPException(status_code=400, detail="Credit card is required")

        card_id = None

        if payment.save_card:
            masked_card = "*" * 12 + payment.credit_card.card_number[-4:]
            existing_card = db.query(CreditCard).filter(
                CreditCard.last_4_numbers == masked_card,
                CreditCard.user_id == current_user.id
            ).first()

            if existing_card is None:
                new_card = CreditCard(
                    user_id=current_user.id,
                    last_4_numbers=masked_card
                )

                db.add(new_card)
                db.flush()
                db.refresh(new_card)

                card_id = new_card.id
            else:
                card_id = existing_card.id

        transaction = Payment(
            user_id=current_user.id,
            order_id=payment.order_id,
            status=PaymentStatus.PENDING,
            credit_card_id=card_id,
        )

        db.add(transaction)

        try:
            db.commit()
            db.refresh(transaction)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Payment processing error")

        return {"status": f"{PaymentStatus.PENDING}", "receipt": transaction.id}
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
