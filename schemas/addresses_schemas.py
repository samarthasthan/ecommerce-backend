# schemas.py

from pydantic import BaseModel
from typing import List


class AddressCreate(BaseModel):
    user_id:str
    name: str
    phone: int
    pincode: int
    state: str
    locality: str
    town: str
    city: str
    type: bool  # True for home address, False for work address
    is_default: bool

    class Config:
        from_attributes = True

class AddressUpdate(BaseModel):
    name: str
    phone: int
    pincode: int
    state: str
    locality: str
    town: str
    city: str
    type: bool  # True for home address, False for work address
    is_default: bool

    class Config:
        from_attributes = True

