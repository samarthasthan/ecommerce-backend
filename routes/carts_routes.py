from dataclasses import Field
from typing import List
from fastapi import APIRouter, Depends, Form
from database import SessionLocal, get_db
from routes.authentication_routes import verify_token
from schemas import carts_schemas
import models

router = APIRouter(tags=["Cart"])


@router.get('/cart',response_model=List[carts_schemas.CartOut])
async def get_cart(email: str = Depends(verify_token),db:SessionLocal=Depends(get_db)):
    cart = db.query(models.Cart).join(models.User).filter(models.User.email == email).all()
    return cart

@router.post("/cart")
async def add_products_to_cart(
    details: carts_schemas.CartBase, db: SessionLocal = Depends(get_db)
):
    new_item= models.Cart(**details.dict())
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
    db.commit()
    db.refresh(cart)
    return cart


@router.delete("/cart")
async def delete_cart_item(
    product:carts_schemas.CartDelete,email: str = Depends(verify_token), db: SessionLocal = Depends(get_db)
):
    cart = db.query(models.Cart).filter(models.Cart.product_id == product.product_id).join(models.User).filter(models.User.email == email).first()
    db.delete(cart)
    db.commit()
    return cart



