# product_routes.py

import os
import uuid
from PIL import Image
from constants import base_url
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from database import SessionLocal, get_db
from models import Product, Category, ProductDetail, BulletPoint, ProductImage
from schemas.products_schemas import (
    BulletPointSchema, ProductCreate, ProductDetailCreate, BulletPointCreate, ProductDetailSchema, ProductImageSchema, ProductListResponse, ProductSchema
)

router = APIRouter(tags=['Product'])

@router.get("/images/products/{product_id}/{size}/{image_name}")
def get_product_image(product_id: str, size: str, image_name: str):
    valid_sizes = ["small", "medium", "large"]
    if size not in valid_sizes:
        raise HTTPException(status_code=400, detail="Invalid image size")

    image_path = f"images/products/{product_id}/{size}/{image_name}"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)

@router.get("/products", response_model=ProductListResponse)
def get_products(db: SessionLocal = Depends(get_db)):
    products = db.query(Product).all()

    response_data = {
        "products": []
    }
     
    for product in products:
        product_details = []
        for detail in product.product_details:
            bullet_points = []
            for bullet in detail.bullet_points:
                bullet_points.append(BulletPointSchema(bullet_id=bullet.bullet_id, point=bullet.point))
            product_details.append(ProductDetailSchema(detail_id=detail.detail_id, heading=detail.heading, bullet_points=bullet_points))

        product_images = []
        for image in product.product_images:
            product_images.append(ProductImageSchema(
                image_id=image.image_id,
                small_image_url=base_url + image.small_image_url,
                medium_image_url=base_url + image.medium_image_url,
                large_image_url=base_url + image.large_image_url
            ))
        response_data["products"].append(ProductSchema(
            product_id=product.product_id,
            product_name=product.product_name,
            product_description=product.product_description,
            regular_price=product.regular_price,
            sale_price=product.sale_price,
            stock_quantity=product.stock_quantity,
            product_details=product_details,
            product_images=product_images
        ))

    return response_data


@router.get("/products/{product_id}")
def read_product(product_id: str, db: SessionLocal = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories/{category_id}/products/")
def get_products_by_category(category_id: str, db: SessionLocal = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    products = category.products
    return products

@router.post("/products/")
def create_product(product: ProductCreate, db: SessionLocal = Depends(get_db)):
    category_ids = product.categories

    # Fetch categories from the database based on the provided category IDs
    categories = db.query(Category).filter(Category.category_id.in_(category_ids)).all()

    if not categories:
        raise HTTPException(status_code=400, detail="Categories not found")

    new_product = Product(
        product_name=product.product_name,
        product_description=product.product_description,
        regular_price=product.regular_price,
        sale_price=product.sale_price,
        stock_quantity=product.stock_quantity,
        categories=categories  # Assign the fetched categories here
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.post("/products/{product_id}/details/")
def add_product_detail(product_id: str, product_detail: ProductDetailCreate, db: SessionLocal = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_detail = ProductDetail(**product_detail.dict(), product=product)
    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail

@router.post("/products/details/{detail_id}/bulletpoints/")
def add_bullet_points(detail_id: str, bullet_points: List[BulletPointCreate], db: SessionLocal = Depends(get_db)):
    product_detail = db.query(ProductDetail).filter(ProductDetail.detail_id == detail_id).first()
    if not product_detail:
        raise HTTPException(status_code=404, detail="Product Detail not found")
    
    new_bullet_points = []
    for bullet_point_data in bullet_points:
        bullet_point = BulletPoint(**bullet_point_data.dict(), product_detail=product_detail)
        db.add(bullet_point)
        new_bullet_points.append(bullet_point)
    
    db.commit()
    return new_bullet_points



def save_resized_image(image_data, size, image_path):
    with Image.open(image_data) as img:
        img.thumbnail(size)
        img.save(image_path, "JPEG")

def save_images_for_product(images, product_id):
    base_folder = "images"
    uploaded_images = []

    for image in images:
        image_data = image.file
        image_extension = image.filename.split(".")[-1]
        
        image_folder = os.path.join(base_folder, "products", product_id)
        small_image_folder = os.path.join(image_folder, "small")
        medium_image_folder = os.path.join(image_folder, "medium")
        large_image_folder = os.path.join(image_folder, "large")

        if not os.path.exists(small_image_folder):
            os.makedirs(small_image_folder)
        if not os.path.exists(medium_image_folder):
            os.makedirs(medium_image_folder)
        if not os.path.exists(large_image_folder):
            os.makedirs(large_image_folder)

        image_name = f"{uuid.uuid4()}.{image_extension}"
        
        small_image_path = os.path.join(small_image_folder, image_name)
        medium_image_path = os.path.join(medium_image_folder, image_name)
        large_image_path = os.path.join(large_image_folder, image_name)

        save_resized_image(image_data, (600, 600), small_image_path)
        save_resized_image(image_data, (900, 900), medium_image_path)
        save_resized_image(image_data, (1200, 1200), large_image_path)

        new_image = ProductImage(product_id=product_id,
                                 small_image_url=small_image_path,
                                 medium_image_url=medium_image_path,
                                 large_image_url=large_image_path)
        uploaded_images.append(new_image)

    return uploaded_images

@router.post("/products/images/")
def upload_product_images(product_id: str, images: List[UploadFile] = File(...),
                          db: SessionLocal = Depends(get_db)):
    uploaded_images = save_images_for_product(images, product_id)
    
    for image in uploaded_images:
        db.add(image)

    db.commit()
    return uploaded_images