from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Category, Product
from db.shemas import CategoryBase, CategoryResponse, ProductResponse, ProductCreate, ProductUpdate

router = APIRouter()

@router.post("/categories", response_model=CategoryResponse)
def add_category(category: CategoryBase, db: Session = Depends(get_db)):
    if category is None:
        raise HTTPException(status_code=404, detail="Please enter a valid category dane")

    if category not in db.query(Category).all():
        db_category = Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        return db_category
    return HTTPException(status_code=404, detail="Category haven`been created")

@router.put("/categories/{id}", response_model=CategoryResponse)
def update_category(
        id: int,
        category: CategoryBase,
        db: Session = Depends(get_db),
):
    db_category = db.query(Category).get(id)

    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if db_category.id == id:

        if category is None:
            raise HTTPException(status_code=404, detail="Please enter a valid category dane")

        updated_category = category.model_dump(exclude_unset=True)

        for key, value in updated_category.items():
            setattr(db_category, key, value)

        db.commit()

    return db_category

@router.delete("/categories/{id}", response_model=CategoryResponse)
def delete_category(
        id: int,
        db: Session = Depends(get_db),
):
    if not id:
        raise HTTPException(status_code=404, detail="Please enter id")

    db_category = db.query(Category).get(id)

    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    db.delete(db_category)
    db.commit()

    return db_category




