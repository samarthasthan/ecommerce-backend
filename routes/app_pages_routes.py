from typing import List
from fastapi import APIRouter, Depends

from database import SessionLocal, get_db
import models
from schemas import app_pages_schemas

router = APIRouter(tags=["App PAGES"])


@router.get('/app/pages',response_model=List[app_pages_schemas.PageOut])
async def get_pages_list(db:SessionLocal=Depends(get_db)):
    pages = db.query(models.Page).all()
    return pages

@router.get('/app/pages/title',response_model=app_pages_schemas.PageOut)
async def get_pages_by_title(page_title:str,db:SessionLocal=Depends(get_db)):
    pages = db.query(models.Page).filter(models.Page.page_title==page_title).first()
    return pages

@router.post('/app/page')
async def create_page(page:app_pages_schemas.PagesBase,db:SessionLocal=Depends(get_db)):
    new_page = models.Page(**page.dict())
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    return new_page

@router.post('/app/page/widget')
async def create_page_widget(page:app_pages_schemas.WidgetsBase,db:SessionLocal=Depends(get_db)):
    new_widget = models.Widget(**page.dict())
    db.add(new_widget)
    db.commit()
    db.refresh(new_widget)
    return new_widget

@router.post('/app/page/widget/item')
async def create_page_widget_item(page:app_pages_schemas.WidgetsItemsBase,db:SessionLocal=Depends(get_db)):
    new_widget_item = models.WidgetItem(**page.dict())
    db.add(new_widget_item)
    db.commit()
    db.refresh(new_widget_item)
    return new_widget_item
