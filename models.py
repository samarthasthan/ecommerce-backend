from secrets import token_hex
from sqlalchemy import Column, ForeignKey,Integer,String,Date,Double
from database import Base
from sqlalchemy.orm import relationship

def generate_uuid():
    return token_hex(16)

class Role(Base):
    __tablename__="roles"

    role_id=Column(String,primary_key=True,default=generate_uuid,index=True)
    role_title=Column(String,nullable= False)
    role_desc=Column(String,nullable= False)


class User(Base):
    __tablename__="users"

    user_id=Column(String,primary_key=True,default=generate_uuid,index=True)

    first_name = Column(String,nullable= False)
    middle_name=Column(String,nullable= False)
    last_name=Column(String,nullable= False)
    email=Column(String,nullable= False)
    phone=Column(Integer,nullable= False)
    role_id=Column(String, ForeignKey('roles.role_id'))

