from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from typing import List
from db.database import get_db
from db.models import Category, Product, User
from db.shemas import CategoryBase, ProductBase, CategoryResponse, ProductResponse, ProductCreate, ProductUpdate

router = APIRouter()

@router.post("/categories", response_model=CategoryResponse)
def add_product(category: CategoryBase, db: Session = Depends(get_db)):
    dict_category = category.model_dump()

    db_category = Category(**dict_category)
    db.add(db_category)
    db.commit()
    return db_category

@router.put("/categories/{id}", response_model=CategoryResponse)
def update_product(
        id: int,
        category: CategoryBase,
        db: Session = Depends(get_db),
):
    if category.id != id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    db_category = category.model_dump(exclude_unset=True)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category

@router.delete("/categories/{id}", response_model=CategoryResponse)
def delete_product(
        id: int,
        db: Session = Depends(get_db),
):
    db_category = db.query(Category).get(id)

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    db.delete(db_category)
    db.commit()
    return db_category


@router.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())

    if not db_product:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Product not found")

    db.add(db_product)
    db.commit()

    return db_product



