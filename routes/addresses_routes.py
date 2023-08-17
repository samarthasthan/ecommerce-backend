# address_routes.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal, get_db
from models import Address
from schemas.addresses_schemas import AddressCreate,AddressUpdate

router = APIRouter(tags=['Address'])

@router.post("/addresses/")
def create_address( address: AddressCreate, db: SessionLocal = Depends(get_db)):
    new_address = Address(**address.dict())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

@router.get("/addresses/")
def read_addresses(user_id: str,db: SessionLocal = Depends(get_db)):
    addresses = db.query(Address).filter(Address.user_id == user_id).all()
    return addresses

@router.get("/addresses/{address_id}")
def read_address(user_id: str, address_id: str, db: SessionLocal = Depends(get_db)):
    address = db.query(Address).filter(Address.user_id == user_id, Address.address_id == address_id).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

@router.put("/addresses/{address_id}")
def update_address(user_id: str, address_id: str, address: AddressUpdate, db: SessionLocal = Depends(get_db)):
    existing_address = db.query(Address).filter(Address.user_id == user_id, Address.address_id == address_id).first()
    if existing_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    for key, value in address.dict().items():
        setattr(existing_address, key, value)
    
    db.commit()
    db.refresh(existing_address)
    return existing_address

@router.delete("/addresses/{address_id}")
def delete_address(user_id: str, address_id: str, db: SessionLocal = Depends(get_db)):
    address = db.query(Address).filter(Address.user_id == user_id, Address.address_id == address_id).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return address
