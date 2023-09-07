from pydantic import BaseModel


class WishListIn(BaseModel):
    product_id:str
    user_id:str
