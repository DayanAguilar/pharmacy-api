from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProductIn(BaseModel):
    category: str
    product: str
    laboratory: str
    buy_price: float
    sell_price: float
    stock: int
    expire_date: Optional[date] = None
    alert_date: Optional[date] = None

class ProductOut(ProductIn):
    product_id: int
