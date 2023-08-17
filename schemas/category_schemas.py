from pydantic import BaseModel
from typing import List, Optional

class CategoryBase(BaseModel):
    category_name: str
    category_description: Optional[str] = None
    parent_category_id: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: str

    class Config:
        from_attributes = True