from typing import List
from fastapi import APIRouter,Depends,HTTPException
from database import SessionLocal,get_db
from schemas import roles_schemas
import models

router = APIRouter(tags=['Roles'])


@router.post('/role',response_model=roles_schemas.RoleOut)
async def create_role(role:roles_schemas.RoleIn,db:SessionLocal=Depends(get_db)):
    role = db.query(models.Role).filter(models.Role.role_title==role.role_title).first()
    if role:
       raise HTTPException(status_code=409, detail="Role with this title already exists")
    else:
     new_role = models.Role(**role.model_dump())
     db.add(new_role)
     db.commit()
     db.refresh(new_role)
     return new_role
    

@router.get('/role',response_model=List[roles_schemas.RoleOut])
async def get_roles(db:SessionLocal=Depends(get_db)):
   roles = db.query(models.Role).all()
   return roles