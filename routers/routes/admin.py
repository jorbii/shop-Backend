from fastapi import HTTPException, APIRouter, Depends, status
from db.shemas import CategoryBase, CategoryResponse
from routers.repositories.dependencies import get_category_repository
from routers.repositories import CategoryRepository

router = APIRouter()


@router.post("/categories", response_model=CategoryResponse)
async def add_category(
    category: CategoryBase,
    repo: CategoryRepository = Depends(get_category_repository)
):
    """Додати нову категорію"""
    if category is None:
        raise HTTPException(status_code=404, detail="Please enter a valid category dane")

    # Перевірка на дублікати (опціонально)
    all_categories = await repo.get_all()
    category_dict = category.model_dump()
    
    # Перевіряємо чи категорія з такою назвою вже існує
    for cat in all_categories:
        if cat.name == category_dict.get('name'):
            raise HTTPException(status_code=400, detail="Category with this name already exists")

    db_category = await repo.create(**category.model_dump())
    await repo.db.commit()
    await repo.db.refresh(db_category)
    return db_category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryBase,
    repo: CategoryRepository = Depends(get_category_repository)
):
    """Оновити категорію"""
    db_category = await repo.get_by_id(category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category is None:
        raise HTTPException(status_code=404, detail="Please enter a valid category dane")

    updated_category = await repo.update(
        category_id,
        **category.model_dump(exclude_unset=True)
    )
    await repo.db.commit()
    await repo.db.refresh(updated_category)

    return updated_category


@router.delete("/categories/{id}", response_model=CategoryResponse)
async def delete_category(
    id: int,
    repo: CategoryRepository = Depends(get_category_repository)
):
    """Видалити категорію"""
    if not id:
        raise HTTPException(status_code=404, detail="Please enter id")

    db_category = await repo.get_by_id(id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    success = await repo.delete(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    await repo.db.commit()
    return db_category
