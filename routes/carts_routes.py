from dataclasses import Field
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException
from database import SessionLocal, get_db
from routes.authentication_routes import verify_token
from schemas import carts_schemas
import models
from constants import base_url

router = APIRouter(tags=["Cart"])


@router.get('/cart')
async def get_cart(email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)):
    cart_products = (
        db.query(models.Product)
        .join(models.Cart, models.Product.product_id == models.Cart.product_id)
        .join(models.User,models.User.user_id==models.Cart.user_id)
        .filter(models.User.email==email)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .all()
    )

    cart_products = [
        {
            "cart_id":product.carts[0].cart_id,
            "sku_id":product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "quantity": product.carts[0].quantity,
            "current_variation": product.carts[0].variation_item_id,
            "all_variation_items": [variation_item for variation_item in product.variations[0].variation_items]
        }
        for product in cart_products
    ]

    return cart_products


@router.post("/cart")
async def add_products_to_cart(
    details: carts_schemas.CartBase,email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)
):
    
    if email:
        new_item= models.Cart(**details.dict())
        new_item.quantity=1
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@router.patch("/cart")
async def change_product_quantity(
    updates:carts_schemas.CartUpdate,email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)
):
    cart = db.query(models.Cart).filter(models.Cart.product_id == updates.product_id).join(models.User).filter(models.User.email == email).first()
    cart.quantity=updates.quantity
    cart.variation_item_id=updates.variation_item_id
    db.commit()
    db.refresh(cart)
    cart_products = (
        db.query(models.Product)
        .join(models.Cart, models.Product.product_id == models.Cart.product_id)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .all()
    )

    cart_products = [
        {
            "cart_id":product.carts[0].cart_id,
            "sku_id":product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "quantity": product.carts[0].quantity,
            "current_variation": product.carts[0].variation_item_id,
            "all_variation_items": [variation_item for variation_item in product.variations[0].variation_items]
        }
        for product in cart_products
    ]

    return cart_products


@router.delete("/cart")
async def delete_cart_item(
    product: carts_schemas.CartDelete,
    email: str = Depends(verify_token),
    db: SessionLocal = Depends(get_db)
):
    # Check if the item exists in the cart
    cart = db.query(models.Cart).filter(
        models.Cart.product_id == product.product_id
    ).join(models.User).filter(models.User.email == email).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Item not found in the cart")

    # Delete the item from the cart
    db.delete(cart)
    db.commit()

    cart_products = (
        db.query(models.Product)
        .join(models.Cart, models.Product.product_id == models.Cart.product_id)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .all()
    )

    cart_products = [
        {
            "cart_id":product.carts[0].cart_id,
            "sku_id":product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "quantity": product.carts[0].quantity,
            "current_variation": product.carts[0].variation_item_id,
            "all_variation_items": [variation_item for variation_item in product.variations[0].variation_items]
        }
        for product in cart_products
    ]

    return cart_products








