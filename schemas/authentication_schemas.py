from pydantic import BaseModel

class UserBase(BaseModel):
    first_name:str
    last_name:str
    email:str
    phone:int

class UserCredentialBase(BaseModel):
    password:str

class UserDetailsBase(BaseModel):
    role_id:str
    otp_secret:str
    otp_verified:bool
    is_active:bool

class UserRegister(UserCredentialBase,UserBase):
    pass

class UserOTPVerifyIn(BaseModel):
    email:str
    otp:str

class UserLogin(BaseModel):
    email:str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str

