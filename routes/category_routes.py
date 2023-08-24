from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from database import get_db
from models import Category
from schemas.category_schemas import CategoryCreate, CategoryUpdate

router = APIRouter(tags=['Category'])

@router.post("/categories/")
def create_category(category: CategoryCreate, db: SessionLocal = Depends(get_db)):
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories/")
def read_categories(db: SessionLocal = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@router.get("/categories/parent/{category_id}")
def read_category_by_parent(parent_category_id: str, db: SessionLocal = Depends(get_db)):
    category = db.query(Category).filter(Category.parent_category_id == parent_category_id).all()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/categories/{category_id}")
def read_category(category_id: str, db: SessionLocal = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}")
def update_category(category_id: str, category: CategoryUpdate, db: SessionLocal = Depends(get_db)):
    existing_category = db.query(Category).filter(Category.category_id == category_id).first()
    if existing_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.dict().items():
        setattr(existing_category, key, value)
    
    db.commit()
    db.refresh(existing_category)
    return existing_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: str, db: SessionLocal = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return category
