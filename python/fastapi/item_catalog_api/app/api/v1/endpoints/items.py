from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select  # SELECT query builder
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import ItemCreate, ItemResponse
from app.db.models import ItemModel
from app.db.session import get_db

router = APIRouter()

@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):

    db_item = ItemModel(**item.model_dump())
    
    db.add(db_item)
    await db.commit()


    await db.refresh(db_item)
    
    return db_item

@router.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(ItemModel).where(ItemModel.id == item_id))
    db_item = result.scalar_one_or_none() 
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return db_item