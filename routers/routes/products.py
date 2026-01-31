from fastapi import HTTPException, APIRouter, Depends
from typing import List
from db.shemas import ProductResponse, ComparisonProductsResponse
from routers.routes.auth import get_current_user
from routers.repositories.dependencies import (
    get_product_repository,
    get_comparison_repository
)
from routers.repositories import ProductRepository, ComparisonRepository
from db.models import User

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def products(
    repo: ProductRepository = Depends(get_product_repository)
):
    """Отримати всі продукти"""
    all_products = await repo.get_all()
    return all_products or []


@router.get("/comparison", response_model=List[ComparisonProductsResponse])
async def show_comparison_table(
    current_user: User = Depends(get_current_user),
    repo: ComparisonRepository = Depends(get_comparison_repository)
):
    """Показати таблицю порівняння продуктів"""
    db_comparison = await repo.get_by_user_id(current_user.id)
    return db_comparison or []


@router.get("/search", response_model=List[ProductResponse])
async def search_product(
    q: str | None,
    repo: ProductRepository = Depends(get_product_repository)
):
    """Пошук продуктів"""
    if q is None:
        return []
    
    search_products = await repo.search(q)
    return search_products or []


@router.get("/{id}", response_model=ProductResponse)
async def one_product(
    id: int,
    repo: ProductRepository = Depends(get_product_repository)
):
    """Отримати один продукт за ID"""
    product = await repo.get_by_id(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{id}/comparison")
async def related_products(
    id: int,
    current_user: User = Depends(get_current_user),
    product_repo: ProductRepository = Depends(get_product_repository),
    comparison_repo: ComparisonRepository = Depends(get_comparison_repository)
):
    """Додати продукт до таблиці порівняння"""
    product = await product_repo.get_by_id(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await comparison_repo.create(user_id=current_user.id, product_id=id)
    await comparison_repo.db.commit()
    return "Product has been added into the comparison table"
