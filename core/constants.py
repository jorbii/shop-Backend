from fastapi import HTTPException, APIRouter, Depends, status
from db.enums import *

router = APIRouter()

@router.get("/utils/enums")
def get_enums():
    return {
        "order_status": [e.value for e in OrderStatus],
        "payment_status": [e.value for e in PaymentStatus],
        "payment_type": [e.value for e in PaymentType]
    }