from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
   return {"msg": "Hello Vinny", "v": "0.2"}


from typing import Optional

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
