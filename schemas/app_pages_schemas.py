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
    has_header:bool
    has_background:bool
    header:str
    background:str
    items_height:float
    items_width:float

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
    has_header:bool
    has_background:bool
    header:str
    background:str
    items_height:float
    items_width:float
    widget_items:List[WidgetsItemsOut]

class PageOut(BaseModel):
    page_title:str
    page_id:str
    widgets:List[WidgetsOut]

class SampleWidget(BaseModel):
    widget_type: str
    items_height: int
    items_width: int
    items_count: int

class SampleWidgetConfiguration(BaseModel):
    widget: SampleWidget



