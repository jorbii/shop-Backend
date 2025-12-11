# db/db.py

class FakeDatabase:
    def __init__(self):
        # 1. Users
        self.users = [
            {"id": 1, "username": "admin_max", "email": "admin@example.com", "password": "pass", "role": "admin", "is_active": True},
            {"id": 2, "username": "simple_user", "email": "user@example.com", "password": "pass", "role": "user", "is_active": True},
            {"id": 3, "username": "blocked_guy", "email": "block@example.com", "password": "pass", "role": "user", "is_active": False},
        ]

        # 2. Categories
        self.categories = [
            {"id": 1, "name": "Electronics", "slug": "electronics"},
            {"id": 2, "name": "Clothing", "slug": "clothing"},
            {"id": 3, "name": "Books", "slug": "books"}
        ]

        # 3. Products
        self.products = [
            {"id": 1, "name": "Laptop Pro", "price": 1200.0, "category_id": 1, "stock": 5},
            {"id": 2, "name": "Smartphone X", "price": 800.0, "category_id": 1, "stock": 10},
            {"id": 3, "name": "T-Shirt", "price": 25.0, "category_id": 2, "stock": 100},
        ]

        # 4. Cart
        self.cart = [
            {"id": 1, "user_id": 2, "items": [{"product_id": 2, "quantity": 1}]}
        ]

        # 5. Orders
        self.orders = [
            {"id": 1, "user_id": 2, "status": "completed", "total_price": 1200.0}
        ]

        # 6. Payments
        self.payments = [
            {"id": 1, "order_id": 1, "amount": 1200.0, "status": "success"}
        ]

# Створюємо ЕКЗЕМПЛЯР класу.
# Саме цю змінну 'db' ми будемо імпортувати в роутери.
db = FakeDatabase()