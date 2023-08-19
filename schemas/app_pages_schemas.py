from enum import Enum
from typing import List
from pydantic import BaseModel


class PagesBase(BaseModel):
    page_title:str

class WidgetsBase(BaseModel):
    widget_title:str
    widget_type:str
    rank:int
    page_id:str

class WidgetsItemsBase(BaseModel):
    image_url :str
    url:str
    type:str
    rank:int
    widget_id:str

class WidgetsItemsOut(BaseModel):
    image_url :str
    url:str
    type:str
    rank:int

class WidgetsOut(BaseModel):
    widget_title:str
    widget_type:str
    rank:int
    widget_items:List[WidgetsItemsOut]

class PageOut(BaseModel):
    page_title:str
    widgets:List[WidgetsOut]




