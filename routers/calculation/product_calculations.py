from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Product, OrderItem


async def check_product_quantity(
    product_id: int,
    order_item: OrderItem,
    db: AsyncSession
) -> bool:
    """Перевіряє наявність товару на складі. Повертає True якщо товару недостатньо"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        return True  # Товар не знайдено - помилка

    # Перевіряємо чи достатньо товару на складі
    if product.stock_quantity < order_item.quantity:
        return True  # Недостатньо товару
    else:
        return False  # Товару достатньо
