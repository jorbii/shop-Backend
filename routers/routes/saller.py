from fastapi import HTTPException, APIRouter, Depends, status
from db.shemas import ProductResponse, ProductCreate
from routers.repositories.dependencies import get_product_repository
from routers.repositories import ProductRepository

router = APIRouter()


@router.post("/products", response_model=ProductResponse)
async def add_product(
    product: ProductCreate,
    repo: ProductRepository = Depends(get_product_repository)
):
    """Додати новий продукт"""
    if product is None:
        raise HTTPException(status_code=404, detail="Please enter a valid product dane")

    db_product = await repo.create(**product.model_dump())
    await repo.db.commit()
    await repo.db.refresh(db_product)

    return db_product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductCreate,
    repo: ProductRepository = Depends(get_product_repository)
):
    """Оновити продукт"""
    db_product = await repo.get_by_id(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product:
        updated_product = await repo.update(
            product_id,
            **product.model_dump(exclude_unset=True, exclude_defaults=True)
        )
        await repo.db.commit()
        await repo.db.refresh(updated_product)
        return updated_product
    
    raise HTTPException(status_code=404, detail="Product haven't been updated")


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    repo: ProductRepository = Depends(get_product_repository)
):
    """Видалити продукт"""
    success = await repo.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await repo.db.commit()
    return {"message": "Product deleted", "status_code": 204}
