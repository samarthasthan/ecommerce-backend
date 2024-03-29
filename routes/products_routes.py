# product_routes.py

import os
import time
import uuid
from PIL import Image
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from database import SessionLocal, get_db
from models import (
    Product,
    Category,
    ProductDetail,
    BulletPoint,
    ProductImage,
    SKU,
    SKUCategoryAssociation,
    User,
    Cart,
    WishList,
    Variation,
    VariationItem,
)
from schemas.products_schemas import (
    ProductCreate,
    ProductDetailCreate,
    BulletPointCreate,
    ProductVariation,
    SKUOut,
    Filters,
)
import models
from sqlalchemy.orm import joinedload, defer, load_only
from constants import base_url
from utils import verify_token, verify_token_optional


router = APIRouter(tags=["Product"])


@router.get("/images/products/{product_id}/{size}/{image_name}")
def get_product_image(product_id: str, size: str, image_name: str):
    valid_sizes = ["small", "medium", "large"]
    if size not in valid_sizes:
        raise HTTPException(status_code=400, detail="Invalid image size")

    image_path = f"images/products/{product_id}/{size}/{image_name}"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(image_path)


@router.get("/product", response_model=SKUOut)
def get_product(
    sku_id: str, user_id: Optional[str] = None, db: SessionLocal = Depends(get_db)
):
    sku = (
        db.query(SKU)
        .filter(SKU.sku_id == sku_id)  # Filter by SKU ID
        .options(
            joinedload(SKU.products)
            .joinedload(Product.product_details)
            .joinedload(ProductDetail.bullet_points),
            joinedload(SKU.products).joinedload(Product.product_images),
            joinedload(SKU.products)
            .joinedload(Product.variations)
            .joinedload(Variation.variation_items),
        )
        .distinct(SKU.sku_id)  # Ensure only one SKU per product
        .first()
    )

    # Modify the image URLs to include the base URL
    for product in sku.products:
        for image in product.product_images:
            image.small_image_url = f"{base_url}{image.small_image_url}"
            image.medium_image_url = f"{base_url}{image.medium_image_url}"
            image.large_image_url = f"{base_url}{image.large_image_url}"

    # Check if user_id is provided and the products are in the user's cart
    if user_id:
        user_cart_items = (
            db.query(Cart)
            .filter(Cart.user_id == user_id)
            .filter(
                Cart.product_id.in_([product.product_id for product in sku.products])
            )
            .all()
        )
        user_cart_product_ids = {item.product_id for item in user_cart_items}
        for product in sku.products:
            product.in_cart = product.product_id in user_cart_product_ids

    # Check if user_id is provided and the products are in the user's wish list
    if user_id:
        user_wish_items = (
            db.query(WishList)
            .filter(WishList.user_id == user_id)
            .filter(
                WishList.product_id.in_(
                    [product.product_id for product in sku.products]
                )
            )
            .all()
        )
        user_wish_product_ids = {item.product_id for item in user_wish_items}
        for product in sku.products:
            product.in_wishlist = product.product_id in user_wish_product_ids

    return sku


@router.get("/products")
def get_products(
    category_id: str,
    user_id: Optional[str] = None,
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(10, description="Items per page", le=1000),
    db: SessionLocal = Depends(get_db),
):
    # Calculate the offset based on page number and items per page
    offset = (page - 1) * per_page

    products = (
        db.query(Product)
        .join(SKU, SKU.sku_id == Product.sku_id)
        .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
        .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
        # .filter(Category.category_id == category_id)
        .join(Variation, Product.product_id == Variation.product_id)
        .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
        .join(ProductImage, Product.product_id == ProductImage.product_id)
        .distinct(Product.product_id)
        .offset(offset)
        .limit(per_page)
        .all()
    )

    if user_id:
        user_cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
        user_wish_items = db.query(WishList).filter(WishList.user_id == user_id).all()

        user_cart_product_ids = {item.product_id for item in user_cart_items}
        user_wish_product_ids = {item.product_id for item in user_wish_items}

        for product in products:
            product.in_cart = product.product_id in user_cart_product_ids
            product.in_wishlist = product.product_id in user_wish_product_ids

        products = [
            {
                "sku_id": product.sku_id,
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_image": f"{base_url}{product.product_images[0].small_image_url}",
                "regular_price": product.variations[0].variation_items[0].regular_price,
                "sale_price": product.variations[0].variation_items[0].sale_price,
                "in_cart": product.in_cart,
                "in_wishlist": product.in_wishlist,
            }
            for product in products
        ]
    else:
        products = [
            {
                "sku_id": product.sku_id,
                "product_id": product.product_id,
                "product_name": product.product_name,
                "product_image": f"{base_url}{product.product_images[0].small_image_url}",
                "regular_price": product.variations[0].variation_items[0].regular_price,
                "sale_price": product.variations[0].variation_items[0].sale_price,
                "in_cart": False,
                "in_wishlist": False,
            }
            for product in products
        ]

    return products


@router.post("/products")
def get_products(
    category_id: str,
    filters: Optional[List[Filters]] = Body(None, description="Selected filters"),
    colors: Optional[List[str]] = Body(None, description="Selected colors"),
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(10, description="Items per page", le=1000),
    db: SessionLocal = Depends(get_db),
):
    # Calculate the offset based on page number and items per page
    offset = (page - 1) * per_page
    if filters is not None and colors is not None:
        variation_item_name = []
        variation_name = []
        for filter in filters:
            variation_name.append(filter.filter_name)
            for name in filter.filter_item_names:
                variation_item_name.append(name)
        products = (
            db.query(Product)
            .filter(Product.color.in_(colors))
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .filter(Variation.variation_name.in_(variation_name))
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .filter(VariationItem.variation_item_name.in_(variation_item_name))
            .join(ProductImage, Product.product_id == ProductImage.product_id)
            .distinct(Product.product_id)
            .offset(offset)
            .limit(per_page)
            .all()
        )
    elif filters is not None and colors is None:
        variation_item_name = []
        variation_name = []
        for filter in filters:
            variation_name.append(filter.filter_name)
            for name in filter.filter_item_names:
                variation_item_name.append(name)
        products = (
            db.query(Product)
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .filter(Variation.variation_name.in_(variation_name))
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .filter(VariationItem.variation_item_name.in_(variation_item_name))
            .join(ProductImage, Product.product_id == ProductImage.product_id)
            .distinct(Product.product_id)
            .offset(offset)
            .limit(per_page)
            .all()
        )
    elif colors is not None and filters is None:
        products = (
            db.query(Product)
            .filter(Product.color.in_(colors))
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .join(ProductImage, Product.product_id == ProductImage.product_id)
            .distinct(Product.product_id)
            .offset(offset)
            .limit(per_page)
            .all()
        )
    else:
        products = (
            db.query(Product)
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .join(ProductImage, Product.product_id == ProductImage.product_id)
            .distinct(Product.product_id)
            .offset(offset)
            .limit(per_page)
            .all()
        )

    products = [
        {
            "sku_id": product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "regular_price": product.variations[0].variation_items[0].regular_price,
            "sale_price": product.variations[0].variation_items[0].sale_price,
            # "color":product.color,
            # "variation": product.variations,
        }
        for product in products
    ]

    return products


def getOptions(category_id, db, filters, colors):
    if filters is None and colors is not None:
        print("colors only")
        variations_query = (
            db.query(
                Variation.variation_name,
                VariationItem.variation_item_name,
                func.count().label("count"),
            )
            .join(VariationItem, VariationItem.variation_id == Variation.variation_id)
            .join(Product, Product.product_id == Variation.product_id)
            .filter(Product.color.in_(colors))
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Variation.variation_name, VariationItem.variation_item_name)
            .all()
        )
    elif filters is not None and colors is None:
        print("only filters")
        variations_query = (
            db.query(
                Variation.variation_name,
                VariationItem.variation_item_name,
                func.count().label("count"),
            )
            .join(VariationItem, VariationItem.variation_id == Variation.variation_id)
            .join(Product, Product.product_id == Variation.product_id)
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Variation.variation_name, VariationItem.variation_item_name)
            .all()
        )
    elif filters is not None and colors is not None:
        print("Both filters and colors")
        variations_query = (
            db.query(
                Variation.variation_name,
                VariationItem.variation_item_name,
                func.count().label("count"),
            )
            .join(VariationItem, VariationItem.variation_id == Variation.variation_id)
            .join(Product, Product.product_id == Variation.product_id)
            .filter(Product.color.in_(colors))
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Variation.variation_name, VariationItem.variation_item_name)
            .all()
        )
    else:
        print("No filter")
        variations_query = (
            db.query(
                Variation.variation_name,
                VariationItem.variation_item_name,
                func.count().label("count"),
            )
            .join(VariationItem, VariationItem.variation_id == Variation.variation_id)
            .join(Product, Product.product_id == Variation.product_id)
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Variation.variation_name, VariationItem.variation_item_name)
            .all()
        )

    variation_obj = {}
    for variation_name, variation_item_name, count in variations_query:
        if variation_name not in variation_obj:
            variation_obj[variation_name] = []
        variation_obj[variation_name].append(
            {"name": variation_item_name, "product_count": count}
        )

    return variation_obj


@router.post("/products/options")
def get_options(
    category_id: str,
    filters: Optional[List[Filters]] = Body(None, description="Selected filters"),
    colors: Optional[List[str]] = Body(None, description="Selected colors"),
    db: SessionLocal = Depends(get_db),
):
    if filters is None and colors is not None:
        print("colors only")
        options = getOptions(
            category_id=category_id, db=db, filters=None, colors=colors
        )
        color_counts_subquery = (
            db.query(
                Product.color, Product.color_hex, func.count().label("product_count")
            )
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Product.color, Product.color_hex)
            .subquery()
        )
    elif filters is not None and colors is None:
        print("only filters")
        options = getOptions(
            category_id=category_id, db=db, filters=filters, colors=None
        )
        variation_item_name = []
        variation_name = []
        for filter in filters:
            variation_name.append(filter.filter_name)
            for name in filter.filter_item_names:
                variation_item_name.append(name)
        color_counts_subquery = (
            db.query(
                Product.color, Product.color_hex, func.count().label("product_count")
            )
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .filter(VariationItem.variation_item_name.in_(variation_item_name))
            .group_by(Product.color, Product.color_hex)
            .subquery()
        )
    elif filters is not None and colors is not None:
        print("both filters and colors")
        options = getOptions(
            category_id=category_id, db=db, filters=filters, colors=colors
        )
        variation_item_name = []
        variation_name = []
        for filter in filters:
            variation_name.append(filter.filter_name)
            for name in filter.filter_item_names:
                variation_item_name.append(name)
        color_counts_subquery = (
            db.query(
                Product.color, Product.color_hex, func.count().label("product_count")
            )
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .join(Variation, Product.product_id == Variation.product_id)
            .join(VariationItem, Variation.variation_id == VariationItem.variation_id)
            .filter(VariationItem.variation_item_name.in_(variation_item_name))
            .group_by(Product.color, Product.color_hex)
            .subquery()
        )
    else:
        print("No filter")
        options = getOptions(category_id=category_id, db=db, filters=None, colors=None)
        color_counts_subquery = (
            db.query(
                Product.color, Product.color_hex, func.count().label("product_count")
            )
            .join(SKU, SKU.sku_id == Product.sku_id)
            .join(SKUCategoryAssociation, SKUCategoryAssociation.sku_id == SKU.sku_id)
            .join(Category, Category.category_id == SKUCategoryAssociation.category_id)
            # .filter(Category.category_id == category_id)
            .group_by(Product.color, Product.color_hex)
            .subquery()
        )

    # Query to select colors with their counts
    products_color = db.query(
        color_counts_subquery.c.color,
        color_counts_subquery.c.color_hex,
        color_counts_subquery.c.product_count,
    ).all()

    # Format the result
    result = [
        {"color": color, "color_hex": color_hex, "product_count": product_count}
        for color, color_hex, product_count in products_color
    ]

    return {"options": options, "colors": result}


####################################################################
# Post APIs


@router.post("/product")
def create_product(product: ProductCreate, db: SessionLocal = Depends(get_db)):
    category_ids = product.categories

    # Fetch categories from the database based on the provided category IDs
    categories = db.query(Category).filter(Category.category_id.in_(category_ids)).all()

    if not categories:
        raise HTTPException(status_code=400, detail="Categories not found")

    # Create a new SKU
    new_sku = SKU()
    db.add(new_sku)
    db.commit()
    db.refresh(new_sku)

    # Create an association between SKU and categories
    for category in categories:
        sku_category_assoc = SKUCategoryAssociation(
            sku_id=new_sku.sku_id, category_id=category.category_id
        )
        db.add(sku_category_assoc)

    # Create a new product associated with the SKU
    new_product = Product(
        product_name=product.product_name,
        product_description=product.product_description,
        color=product.color,
        color_hex=product.color_hex,
        sku_id=new_sku.sku_id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.post("/product/sku")
def add_product_sku(
    sku_id: str, product: ProductCreate, db: SessionLocal = Depends(get_db)
):
    category_ids = product.categories

    # Fetch categories from the database based on the provided category IDs
    categories = db.query(Category).filter(Category.category_id.in_(category_ids)).all()

    if not categories:
        raise HTTPException(status_code=400, detail="Categories not found")

    # Create a new product associated with the specified SKU
    new_product = Product(
        product_name=product.product_name,
        product_description=product.product_description,
        color=product.color,
        color_hex=product.color_hex,
        sku_id=sku_id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.post("/product/{product_id}/details")
def add_product_detail(
    product_id: str,
    product_detail: ProductDetailCreate,
    db: SessionLocal = Depends(get_db),
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_detail = ProductDetail(**product_detail.dict(), product=product)
    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail


@router.post("/product/details/{detail_id}/bulletpoints")
def add_bullet_points(
    detail_id: str,
    bullet_points: List[BulletPointCreate],
    db: SessionLocal = Depends(get_db),
):
    product_detail = (
        db.query(ProductDetail).filter(ProductDetail.detail_id == detail_id).first()
    )
    if not product_detail:
        raise HTTPException(status_code=404, detail="Product Detail not found")

    new_bullet_points = []
    for bullet_point_data in bullet_points:
        bullet_point = BulletPoint(
            **bullet_point_data.dict(), product_detail=product_detail
        )
        db.add(bullet_point)
        new_bullet_points.append(bullet_point)

    db.commit()
    return new_bullet_points


def save_resized_image(image_data, size, image_path):
    with Image.open(image_data) as img:
        # Convert RGBA to RGB if the image has an alpha channel
        if img.mode == "RGBA":
            img = img.convert("RGB")
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

        new_image = ProductImage(
            product_id=product_id,
            small_image_url=small_image_path,
            medium_image_url=medium_image_path,
            large_image_url=large_image_path,
        )
        uploaded_images.append(new_image)

    return uploaded_images


@router.post("/product/images")
def upload_product_images(
    product_id: str,
    images: List[UploadFile] = File(...),
    db: SessionLocal = Depends(get_db),
):
    uploaded_images = save_images_for_product(images, product_id)

    for image in uploaded_images:
        db.add(image)

    db.commit()
    return uploaded_images


@router.post("/product/variation")
def create_product_variation(
    variation: ProductVariation, db: SessionLocal = Depends(get_db)
):
    # Create a new Variation instance
    new_variation = models.Variation(
        product_id=variation.product_id, variation_name=variation.variation_name
    )

    # Add the new Variation instance to the database session
    db.add(new_variation)
    db.commit()
    db.refresh(new_variation)

    # Create VariationItem instances and add them to the database
    for item in variation.variation_items:
        new_variation_item = models.VariationItem(
            variation_item_name=item.variation_item_name,
            stock=item.stock,
            variation_id=new_variation.variation_id,
            regular_price=item.regular_price,
            sale_price=item.sale_price,
        )
        db.add(new_variation_item)
        db.commit()
        db.refresh(new_variation_item)

    # Return a response indicating success (you can customize this)
    return {"message": "Product variation created successfully"}
