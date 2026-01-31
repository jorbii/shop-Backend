from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from routers.calculation import check_the_cart, calculate_total_price
from db.database import get_async_db
from db.models import User, Cart
from db.shemas import OrderItemResponse, OrderItemCreate, CartResponse
from routers.routes.auth import get_current_user
from routers.repositories.dependencies import (
    get_cart_repository,
    get_product_repository,
    get_order_item_repository
)
from routers.repositories import (
    CartRepository,
    ProductRepository,
    OrderItemRepository
)

router = APIRouter()


@router.get('/', response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Отримати кошик користувача"""
    cart = await cart_repo.get_by_user_id(current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail='No cart found.')
    return cart


@router.post('/item', response_model=OrderItemResponse)
async def add_to_cart(
    order: OrderItemCreate,
    cart: Cart = Depends(check_the_cart),
    product_repo: ProductRepository = Depends(get_product_repository),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Додати товар до кошика"""
    product = await product_repo.get_by_id(order.product_id)
    if not product:
        raise HTTPException(status_code=404, detail='No product found.')

    # Перевіряємо чи вже є такий товар в кошику
    db_order = await order_item_repo.get_by_cart_and_product(cart.id, product.id)

    if db_order:
        # Перевіряємо чи достатньо товару на складі
        if product.stock_quantity < db_order.quantity + order.quantity:
            raise HTTPException(status_code=400, detail='Quantity is already taken.')
        
        # Оновлюємо кількість
        await order_item_repo.add_quantity(db_order, order.quantity)
        await order_item_repo.db.commit()
        await order_item_repo.db.refresh(db_order)

        # Оновлюємо загальну ціну кошика
        cart.total_price = await calculate_total_price(order_item_repo.db, cart)
        await cart_repo.update_total_price(cart, cart.total_price)
        await cart_repo.db.commit()
        return db_order

    # Створюємо новий елемент кошика
    new_order_item = await order_item_repo.create(
        cart_id=cart.id,
        product_id=product.id,
        quantity=order.quantity,
        price_at_purchase=float(product.price)
    )
    await order_item_repo.db.commit()
    await order_item_repo.db.refresh(new_order_item)

    # Оновлюємо загальну ціну кошика
    cart.total_price = await calculate_total_price(order_item_repo.db, cart)
    await cart_repo.update_total_price(cart, cart.total_price)
    await cart_repo.db.commit()

    return new_order_item


@router.put("/item/{item_id}", response_model=CartResponse)
async def change_order_quantity(
    item_id: int,
    quantity: int,
    cart: Cart = Depends(check_the_cart),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Змінити кількість товару в кошику"""
    cart_item = await order_item_repo.get_by_id(item_id)
    if not cart_item or cart_item.cart_id != cart.id:
        raise HTTPException(status_code=404, detail='OrderItem not found.')

    # Перевіряємо чи достатньо товару для нової кількості
    product = await product_repo.get_by_id(cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found.')
    
    new_quantity = cart_item.quantity + quantity
    if product.stock_quantity < new_quantity:
        raise HTTPException(status_code=400, detail='Quantity is already taken.')

    # Оновлюємо кількість
    await order_item_repo.add_quantity(cart_item, quantity)
    await order_item_repo.db.commit()
    await order_item_repo.db.refresh(cart_item)

    # Оновлюємо загальну ціну кошика
    cart.total_price = await calculate_total_price(order_item_repo.db, cart)
    await cart_repo.update_total_price(cart, cart.total_price)
    await cart_repo.db.commit()
    await cart_repo.db.refresh(cart)

    return cart


@router.delete("/item/{item_id}")
async def delete_item_from_cart(
    item_id: int,
    cart: Cart = Depends(check_the_cart),
    order_item_repo: OrderItemRepository = Depends(get_order_item_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Видалити товар з кошика"""
    cart_item = await order_item_repo.get_by_id(item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail='OrderItem not found.')
    
    # Оновлюємо загальну ціну кошика
    cart.total_price -= abs(cart_item.price_at_purchase * cart_item.quantity)
    await order_item_repo.delete(cart_item)
    await order_item_repo.db.commit()
    return f"Item {item_id} was successfully deleted."


@router.delete("/")
async def clear_cart(
    cart: Cart = Depends(check_the_cart),
    cart_repo: CartRepository = Depends(get_cart_repository)
):
    """Очистити кошик"""
    await cart_repo.clear_cart(cart)
    await cart_repo.db.commit()
    return "Cart was successfully cleared."
