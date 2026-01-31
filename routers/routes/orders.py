from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from routers.calculation import order_status, check_the_cart
from db.database import get_async_db
from db.enums import OrderStatus
from db.models import Cart, Product
from db.shemas import OrderResponse, OrderCreate
from routers.repositories.dependencies import (
    get_order_repository,
    get_address_repository,
    get_product_repository,
    get_order_item_repository
)
from routers.repositories import (
    OrderRepository,
    AddressRepository,
    ProductRepository,
    OrderItemRepository
)

router = APIRouter()


@router.post('/', response_model=OrderResponse)
async def create_order(
    address: OrderCreate,
    cart: Cart = Depends(check_the_cart),
    order_repo: OrderRepository = Depends(get_order_repository),
    address_repo: AddressRepository = Depends(get_address_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository)
):
    """Створити нове замовлення"""
    # Отримуємо елементи кошика
    cart_items = await order_repo.get_cart_items(cart.id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Обробка адреси
    address_id = None
    if address.address_id:
        db_address = await address_repo.get_user_address(address.address_id, cart.user_id)
        if not db_address:
            raise HTTPException(status_code=404, detail="Inputted address is not found")
        address_id = db_address.id
    else:
        new_address = await address_repo.create(
            user_id=cart.user_id,
            **address.model_dump(exclude={'address_id'})
        )
        await address_repo.db.flush()
        address_id = new_address.id

    # Створюємо замовлення
    order = await order_repo.create(
        user_id=cart.user_id,
        cart_id=cart.id,
        address_id=address_id,
        total_price=float(cart.total_price)
    )
    await order_repo.db.flush()

    # Перевірка та списання товарів зі складу
    product_ids = [item.product_id for item in cart_items]
    result = await order_repo.db.execute(
        select(Product)
        .where(Product.id.in_(product_ids))
        .with_for_update()
    )
    products_map = {p.id: p for p in result.scalars().all()}

    for item in cart_items:
        product = products_map.get(item.product_id)
        if not product:
            await order_repo.db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.stock_quantity < item.quantity:
            await order_repo.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product '{product.name}'."
            )

        # Списуємо товар зі складу
        await product_repo.decrease_stock(product.id, item.quantity)
        item.order_id = order.id
        order_repo.db.add(item)

    try:
        await order_repo.db.commit()
        await order_repo.db.refresh(order)
        
        # Отримуємо повне замовлення з елементами
        full_order = await order_repo.get_by_id(order.id)
        return full_order

    except Exception as e:
        await order_repo.db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/{order_id}', response_model=OrderResponse)
async def order_info(
    order_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Отримати інформацію про замовлення"""
    order = await order_status(order_id, db)
    return order


@router.patch('/{order_id}')
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_async_db),
    order_repo: OrderRepository = Depends(get_order_repository)
):
    """Скасувати замовлення"""
    from routers.calculation import order_status
    order = await order_status(order_id, db)
    await order_repo.update_status(order, OrderStatus.CANCELLED)
    await order_repo.db.commit()
    return {"message": "Order canceled successfully"}
