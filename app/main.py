from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

rooms = [
    {
        "room_number": 101,
        "type": "Single",
        "price": 80,
        "bookable": True
    },
    {
        "room_number": 102,
        "type": "Double",
        "price": 120,
        "bookable": True
    },
    {
        "room_number": 201,
        "type": "Suite",
        "price": 200,
        "bookable": False
    }
]

@app.get("/")
def read_root():
    return {"msg": "Hello Vinny", "v": "0.2"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api/ip")
def get_ip(request: Request):
    ip = request.client.host if request.client else "unknown"
    return {"ip": ip}

@app.get("/ip", response_class=HTMLResponse)
def get_ip_html(request: Request):
    ip = request.client.host if request.client else "unknown"
    return f"<h1>Your public IP is {ip}</h1>"

@app.get("/rooms")
def get_rooms():
    return rooms
