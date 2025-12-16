from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User, Product, ComparisonProducts
from db.shemas import ProductResponse, ComparisonProductsResponce
from routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).all()

    if not products:
        return []

    return products

@router.get("/comparison", response_model=List[ComparisonProductsResponce])
def show_comparison_table(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comparison = db.query(ComparisonProducts).filter(ComparisonProducts.user_id == current_user.id).all()

    if not db_comparison:
        return []

    return db_comparison


@router.get("/{id}", response_model=ProductResponse)
def one_product(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.post("/{id}/comparison")
def related_products(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = db.query(Product).get(id)

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_comparison = ComparisonProducts(
        user_id = current_user.id,
        product_id = id,
        product = db_product
    )
    db.add(db_comparison)
    db.commit()

    return "Product has been added into the comparison table"

@router.get("/search", response_model=List[ProductResponse])
def search_product(q: str = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not q:
        return []

    search_products = db.query(Product).filter(or_(
                Product.name.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%")
            )).all()

    if not search_products:
        return []

    return search_products

