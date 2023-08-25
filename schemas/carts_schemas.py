from pydantic import BaseModel
from schemas import products_schemas

class CartBase(BaseModel):
    quantity: int
    product_id: str
    user_id: str

class CartOut(BaseModel):
    product:products_schemas.ProductSchema
    quantity:int

    class Config:
        orm_mode = True

class CartUpdate(BaseModel):
    product_id:str
    quantity:int

class CartDelete(BaseModel):
    product_id:str