from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import User, Product, ComparisonProducts
from db.shemas import ProductResponse, ComparisonProductsResponse
from routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    if not products:
        return []

    return products

@router.get("/comparison", response_model=List[ComparisonProductsResponse])
def show_comparison_table(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comparison = db.query(ComparisonProducts).filter(ComparisonProducts.user_id == current_user.id).all()

    if not db_comparison:
        return []

    return db_comparison


@router.get("/search", response_model=List[ProductResponse])
def search_product(q: str | None, db: Session = Depends(get_db)):

    if q is None:
        return []

    search_products = db.query(Product)\
        .filter(or_(Product.name.contains(q.lower()),
        Product.description.contains((q.lower())))).all()

    if search_products is None:
        return []

    return search_products

@router.get("/{id}", response_model=ProductResponse)
def one_product(id: int, db: Session = Depends(get_db)):
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


