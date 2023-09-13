from dataclasses import Field
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException
from database import SessionLocal, get_db
from routes.authentication_routes import verify_token
from schemas import wishlist_schemas
import models
from constants import base_url

router = APIRouter(tags=["WishList"])


@router.post('/wishlist')
async def add_product_to_wishlist(data:wishlist_schemas.WishListIn,email: str = Depends(verify_token),db:SessionLocal=Depends(get_db)):
    new_wishlist = models.WishList(**data.dict())
    db.add(new_wishlist)
    db.commit()
    db.refresh(new_wishlist)
    
    wishlists_products = (
        db.query(models.Product)
        .join(models.WishList, models.Product.product_id == models.WishList.product_id)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .filter(models.User.email == email)
        .distinct(models.Product.product_id)
        .all()
    )

    wishlists_products = [
        {
            "sku_id": product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "regular_price": product.variations[0].variation_items[0].regular_price,
            "sale_price": product.variations[0].variation_items[0].sale_price,
            "variations":product.variations
        }
        for product in wishlists_products
    ]

    return wishlists_products

@router.delete('/wishlist')
async def delete_wishlist_item(data:wishlist_schemas.WishListIn,email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)):
    wishlist_item = (
        db.query(models.WishList)
        .filter(models.WishList.product_id == data.product_id)
        .filter(models.WishList.user_id == data.user_id).first()
    )

    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in the wishlist")

    # Delete the item from the cart
    db.delete(wishlist_item)
    db.commit()

    wishlists_products = (
        db.query(models.Product)
        .join(models.WishList, models.Product.product_id == models.WishList.product_id)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .filter(models.User.email == email)
        .distinct(models.Product.product_id)
        .all()
    )

    wishlists_products = [
        {
            "sku_id": product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "regular_price": product.variations[0].variation_items[0].regular_price,
            "sale_price": product.variations[0].variation_items[0].sale_price,
            "variations":product.variations
        }
        for product in wishlists_products
    ]

    return wishlists_products

@router.get('/wishlist')
async def get_wishlist_items(email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)):
    wishlists_products = (
        db.query(models.Product)
        .join(models.WishList, models.Product.product_id == models.WishList.product_id)
        .join(models.Variation, models.Product.product_id == models.Variation.product_id)
        .join(models.VariationItem, models.Variation.variation_id == models.VariationItem.variation_id)
        .join(models.ProductImage, models.Product.product_id == models.ProductImage.product_id)
        .filter(models.User.email == email)
        .distinct(models.Product.product_id)
        .all()
    )

    wishlists_products = [
        {
            "sku_id": product.sku_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "product_image": f"{base_url}{product.product_images[0].small_image_url}",
            "regular_price": product.variations[0].variation_items[0].regular_price,
            "sale_price": product.variations[0].variation_items[0].sale_price,
            "variations":product.variations
        }
        for product in wishlists_products
    ]

    return wishlists_products
