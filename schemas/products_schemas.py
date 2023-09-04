# product_schemas.py

from pydantic import BaseModel
from typing import List

class ProductCreate(BaseModel):
    product_name: str
    product_description: str
    color:str
    color_hex: str
    categories: List[str]  # List of category IDs

class ProductUpdate(BaseModel):
    product_name: str
    product_description: str
    color: str
    color_hex: str

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

class VariationCreate(BaseModel):
    product_id:str
    variation_name:str

class VariationItemCreate(BaseModel):
    variation_item_name:str
    stock:int
    regular_price: float
    sale_price: float

class ProductVariation(VariationCreate):
    variation_items:List[VariationItemCreate]


##################################################



class BulletPointOut(BaseModel):
    bullet_id: str
    point: str

class ProductDetailOut(BaseModel):
    detail_id: str
    heading: str
    bullet_points: List[BulletPointOut]

class ProductImageOut(BaseModel):
    image_id: str
    small_image_url: str
    medium_image_url: str
    large_image_url: str
    

class VariationItemsOut(BaseModel):
    variation_item_name:str
    stock:int
    regular_price: float
    sale_price: float

class VariationOut(BaseModel):
    variation_name:str
    variation_items:List[VariationItemsOut]

class ProductOut(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    color: str
    color_hex: str
    product_details: List[ProductDetailOut]
    product_images: List[ProductImageOut]
    variations:List[VariationOut]


class SKUOut(BaseModel):
    sku_id:str
    products: List[ProductOut]
