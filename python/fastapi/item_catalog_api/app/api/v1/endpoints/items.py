from fastapi import APIRouter, HTTPException
from app.models.item import ItemCreate, ItemResponse
from app.db.memory_db import add_item, get_item_by_id

router = APIRouter()

@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    new_item = add_item(item)
    return new_item

@router.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int):
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item