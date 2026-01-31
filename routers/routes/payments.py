from fastapi import HTTPException, APIRouter, Depends
from routers.calculation import order_status
from db.enums import PaymentStatus, PaymentType
from db.models import User
from db.shemas import PaymentCreate
from routers.routes.auth import get_current_user
from routers.repositories.dependencies import (
    get_payment_repository,
    get_credit_card_repository,
    get_cart_repository
)
from routers.repositories import (
    PaymentRepository,
    CreditCardRepository,
    CartRepository
)

router = APIRouter()


@router.post("/initiate/{order_id}")
async def create_payment(
    order_id: int,
    payment: PaymentCreate,
    current_user: User = Depends(get_current_user),
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    credit_card_repo: CreditCardRepository = Depends(get_credit_card_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Створити платіж"""
    # Отримуємо замовлення через order_status (використовуємо db з payment_repo)
    order = await order_status(order_id, payment_repo.db)
    if not order:
        raise HTTPException(status_code=400, detail="Order haven`t been found")

    if payment.payment_type == PaymentType.credit_card:
        if payment.credit_card is None:
            raise HTTPException(status_code=400, detail="Credit card is required")

        card_id = None

        if payment.save_card:
            masked_card = "*" * 12 + payment.credit_card.card_number[-4:]
            existing_card = await credit_card_repo.find_by_last_4_numbers(
                current_user.id,
                masked_card
            )

            if existing_card is None:
                new_card = await credit_card_repo.create(
                    user_id=current_user.id,
                    last_4_numbers=masked_card
                )
                await credit_card_repo.db.flush()
                await credit_card_repo.db.refresh(new_card)
                card_id = new_card.id
            else:
                card_id = existing_card.id

        # Створюємо платіж
        transaction = await payment_repo.create(
            user_id=current_user.id,
            order_id=order.id,
            credit_card_id=card_id,
            status=PaymentStatus.PENDING
        )

        # Очищаємо кошик після успішного платежу
        cart = await cart_repo.get_by_user_id(current_user.id)
        if cart:
            await cart_repo.clear_cart(cart)
            await cart_repo.db.commit()

        await payment_repo.db.commit()
        await payment_repo.db.refresh(transaction)

        return {"status": f"{PaymentStatus.PENDING}", "receipt": transaction.id}
    
    return {"msg": "Other methods not implemented yet"}
