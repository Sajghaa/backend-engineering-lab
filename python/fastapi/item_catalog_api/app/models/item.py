from pydantic import BaseModel, ConfigDict

class ItemCreate(BaseModel):
    name: str
    price: float
    is_offer: bool = False

class ItemResponse(ItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)