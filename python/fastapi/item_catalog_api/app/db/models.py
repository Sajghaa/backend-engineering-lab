from sqlalchemy import String, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

# This is the database table representation
class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)  # index for faster search
    price: Mapped[float] = mapped_column(Float)
    is_offer: Mapped[bool] = mapped_column(Boolean, default=False)