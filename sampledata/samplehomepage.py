import subprocess
import json
import random
from typing import List
from fastapi import APIRouter, Depends
from database import SessionLocal, get_db
from schemas import app_pages_schemas
import models
import requests

#  "header": f"https://placehold.co/{height}x{width}/{generate_random_color}/FFF?text={height}x{width}",
#             "background": f"https://placehold.co/500x500/{generate_random_color}/FFF",


router = APIRouter(tags=['Sample data'])


def generate_random_color():
    hex_digits = "0123456789ABCDEF"
    color = ""
    for _ in range(6):
        color += random.choice(hex_digits)
    return color

@router.get("/app/page/delete")
def delete_all_widgets(db:SessionLocal=Depends(get_db)):
    wigets = db.query(models.Widget).all()
    widgets_items=db.query(models.WidgetItem).all()
    for widget in wigets:
        db.delete(widget)
        db.commit()
    for widgets_item in widgets_items:
        db.delete(widgets_item)
        db.commit()
    return "Success"


@router.post("/app/page/sample")
def create_sample_home_widgets(pageid:str,widgets:List[app_pages_schemas.SampleWidgetConfiguration]):
    widget_rank = 0
    for widget in widgets:
        widget_rank = widget_rank + 1
        widget_data = {
            "widget_title": widget.widget.widget_type,  # Use dot notation
            "widget_type": widget.widget.widget_type,  # Use dot notation
            "page_id": pageid,
            "rank": widget_rank,
            "has_header": True,
            "has_background": True,
            "header": f"https://placehold.co/{360}x{50}/{generate_random_color()}/FFF/png?text={widget.widget.widget_type}{' '}{widget_rank}",
            "background": f"https://placehold.co/{360}x{400}/{generate_random_color()}/FFF/png",
            "items_height": widget.widget.items_height,  # Use dot notation
            "items_width": widget.widget.items_width,    # Use dot notation
        }
        widget_json = json.dumps(widget_data)
        curl_command = [
            "curl",
            "-X",
            "POST",
            "http://127.0.0.1:8000/app/page/widget",
            "-H",
            "accept: application/json",
            "-H",
            "Content-Type: application/json",
            "-d",
            widget_json,
        ]
        response = subprocess.run(curl_command, stdout=subprocess.PIPE, text=True)
        response_json = json.loads(response.stdout)
        widget_id = response_json["widget_id"]
        # print(widget_id)
        for widget_item in range(widget.widget.items_count):
            url = "http://127.0.0.1:8000/app/page/widget/item"
            payload = {
                "image_url": f"https://placehold.co/{widget.widget.items_width}x{widget.widget.items_height}/{generate_random_color()}/FFF/png?text={widget_item+1}",
                "url": f"https://placehold.co/{widget.widget.items_width}x{widget.widget.items_height}/{generate_random_color()}/FFF/png?text={widget_item+1}",
                "rank": widget_item + 1,
                "type": "image",
                "widget_id": widget_id,
            }
            # Convert the payload to JSON format
            json_payload = json.dumps(payload)
    
            # # Define headers
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            # Make the POST request using requests
            response = requests.post(url, headers=headers, data=json_payload)
            # Print the response content
            print(response.text)
    return "Success"

