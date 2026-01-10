from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy.orm import Session

from core.constants import order_status, check_the_cart
from db.database import get_db
from db.enums import OrderStatus
from db.models import Order, UserAddress, Cart, Product
from db.shemas import OrderResponse, OrderCreate


router = APIRouter()


@router.post('/', response_model=OrderResponse)
def create_order(address: OrderCreate, cart: Cart = Depends(check_the_cart), db: Session = Depends(get_db)):
    # 1. Фільтруємо товари, які ще не в замовленні
    cart_items = [item for item in cart.items if item.order_id is None] if cart else []

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 2. Логіка адреси (без змін)
    if address.address_id:
        db_address = db.query(UserAddress).filter(UserAddress.id == address.address_id,
                                                  UserAddress.user_id == cart.user_id).scalar()
        if not db_address:
            raise HTTPException(status_code=404, detail="Inputted address is not found")
        address_id = db_address.id
    else:
        new_address = UserAddress(user_id=cart.user_id, **address.model_dump(exclude={'address_id'}))
        db.add(new_address)
        db.flush()  # Використовуємо flush, щоб отримати ID, але не комітити
        address_id = new_address.id

    # 3. Створення об'єкта замовлення
    order = Order(
        user_id=cart.user_id,
        status=OrderStatus.NEW,
        total_price=cart.total_price,
        cart_id=cart.id,
        address_id=address_id
    )
    db.add(order)
    db.flush()  # Отримуємо ID замовлення

    # 4. ПЕРЕВІРКА І СПИСАННЯ ТОВАРІВ (В одній транзакції)
    for item in cart_items:
        # Отримуємо актуальний продукт з БД (з блокуванням на запис, якщо потрібно, але поки просто get)
        product = db.query(Product).filter(Product.id == item.product_id).with_for_update().first()

        if not product:
            db.rollback()  # Скасовуємо все, якщо товару раптом не існує
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.stock_quantity < item.quantity:
            db.rollback()  # ВАЖЛИВО: Скасовуємо створення адреси і замовлення
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product '{product.name}'. Available: {product.stock_quantity}"
            )

        # Списуємо кількість (але поки НЕ робимо commit)
        product.stock_quantity -= item.quantity
        db.add(product)

        # Прив'язуємо товар до замовлення
        item.order_id = order.id
        db.add(item)

    try:
        # 5. Фінальний коміт всього: адреси, замовлення, списання товарів
        db.commit()
        db.refresh(order)
        return order

    except Exception as e:
        db.rollback()  # У разі будь-якої іншої помилки — все скасовуємо
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/{order_id}', response_model=OrderResponse)
def order_info(order: Order = Depends(order_status)):
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