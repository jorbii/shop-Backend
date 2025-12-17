from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Product
from db.shemas import ProductResponse, ProductCreate



router = APIRouter()

@router.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    if product is None:
        raise HTTPException(status_code=404, detail="Please enter a valid product dane")

    db_product = Product(**product.model_dump())

    if not db_product:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Product not found")

    db.add(db_product)
    db.commit()

    return db_product

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product:
        new_schema_product = product.model_dump(exclude_unset=True, exclude_defaults=True)

        for key, value in new_schema_product.items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)

        return db_product
    return HTTPException(status_code=404, detail="Product haven't been updated")

























