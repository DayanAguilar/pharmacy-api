from pydantic import BaseModel
from typing import Optional
from datetime import date
import datetime
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
    
class SellIn(BaseModel):
    product_id: int
    quantity: int = 0

class SellOut(SellIn):
    sell_id: Optional[int] = None
    date: datetime.date
    total_price: float = 0
    product: str = "Unknown Product"