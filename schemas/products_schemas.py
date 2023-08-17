# product_schemas.py

from pydantic import BaseModel
from typing import List

class ProductCreate(BaseModel):
    product_name: str
    product_description: str
    regular_price: float
    sale_price: float
    stock_quantity: int
    categories: List[str]  # List of category IDs

class ProductUpdate(BaseModel):
    product_name: str
    product_description: str
    regular_price: float
    sale_price: float
    stock_quantity: int

class CategoryCreate(BaseModel):
    category_name: str
    category_description: str
    parent_category_id: str = None

class ProductDetailCreate(BaseModel):
    heading: str

class BulletPointCreate(BaseModel):
    point: str

class ProductImageCreate(BaseModel):
    image_type: str
    image_url: str

##################################################



class BulletPointSchema(BaseModel):
    bullet_id: str
    point: str

class ProductDetailSchema(BaseModel):
    detail_id: str
    heading: str
    bullet_points: List[BulletPointSchema]

class ProductImageSchema(BaseModel):
    image_id: str
    small_image_url: str
    medium_image_url: str
    large_image_url: str

class ProductSchema(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    regular_price: float
    sale_price: float
    stock_quantity: int
    product_details: List[ProductDetailSchema]
    product_images: List[ProductImageSchema]

class ProductListResponse(BaseModel):
    products: List[ProductSchema]