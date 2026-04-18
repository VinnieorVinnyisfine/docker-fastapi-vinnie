from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

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
