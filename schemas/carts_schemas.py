from pydantic import BaseModel
from schemas import products_schemas

class CartBase(BaseModel):
    product_id: str
    user_id: str
    variation_item_id:str

class CartProductOut(BaseModel):
    product_name:str

class CartOut(BaseModel):
    product:CartProductOut
    
    quantity:int

    class Config:
        orm_mode = True

class CartUpdate(BaseModel):
    product_id:str
    quantity:int
    variation_item_id:str

class CartDelete(BaseModel):
    product_id:str