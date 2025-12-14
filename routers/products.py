from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from typing import List

from db.database import get_db
from db.models import User, Product
from db.shemas import ProductCreate, ProductUpdate, ProductBase, ProductResponse
from routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    products = db.query(Product).all()

    if not products:
        raise HTTPException(status_code=404, detail="Product not found")

    return products

@router.get("/{id}", response_model=ProductResponse)
def one_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).get(id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# @router.post("/{id}/related", response_model=ProductResponse)
# def related_products(id: int, db: Session = Depends(get_db)):

