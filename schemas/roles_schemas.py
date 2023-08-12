from pydantic import BaseModel


class RoleIn(BaseModel):
    role_title:str
    role_desc:str

class RoleOut(BaseModel):
    role_id:str
    role_title:str
    role_desc:str