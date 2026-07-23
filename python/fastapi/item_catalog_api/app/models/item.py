from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float
    is_offer: bool = False


class ItemResponse(ItemCreate):
    id: int