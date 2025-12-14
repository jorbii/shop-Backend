import uvicorn
from fastapi import FastAPI

from routers import (
    auth,
    users,
    products,
    cart,
    categories,
    orders,
    payments,
    admin
)
from db.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="My E-commerce API",
    description="API магазинчику на імітації DB",
    version="0.1.0"
)

# --- Підключення роутерів ---
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

# 1. Users
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# 2. Products
app.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)
#
# # 3. Categories
# app.include_router(
#     categories.router,
#     prefix="/categories",
#     tags=["Categories"]
# )
#
# # 4. Cart
# app.include_router(
#     cart.router,
#     prefix="/cart",
#     tags=["Cart"]
# )

# 5. Orders
# app.include_router(
#     orders.router,
#     prefix="/orders",
#     tags=["Orders"]
# )

# 6. Payments
# app.include_router(
#     payments.router,
#     prefix="/payments",
#     tags=["Payments"]
# )
#
# 7. Admin (окремі адмінські штуки)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)


# Простий рут для перевірки, чи сервер живий
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce API! Go to /docs for Swagger UI."}


if __name__ == "__main__":
    # Запуск сервера, якщо файл запускається напряму
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)