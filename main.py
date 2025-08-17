from product_service import ProductService
from product import Product
from sell_service import SellService
from sell import Sell
import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
from pydantic_models import ProductIn, ProductOut
load_dotenv()
POSTGRESS_SQL_URL = os.environ["POSTGRESS_SQL_URL"]

conn = psycopg2.connect(POSTGRESS_SQL_URL)
product_service = ProductService(conn)
sell_service = SellService(conn)

app = FastAPI()


@app.get("/products")
def get_products():
    try:
        products = product_service.get_all_products()
        return [p.to_dict() for p in products]
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": str(e)})

@app.post("/products", response_model=ProductOut)
def create_product(product: ProductIn):
    try:
        # convertir de ProductIn (Pydantic) → Product (tu clase)
        product_obj = Product(
            product_id=None,  # autoincrement
            category=product.category,
            product=product.product,
            laboratory=product.laboratory,
            buy_price=product.buy_price,
            sell_price=product.sell_price,
            stock=product.stock,
            expire_date=product.expire_date,
            alert_date=product.alert_date
        )
        product_id = product_service.create_product(product_obj)
        product_obj.product_id = product_id
        return product_obj.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))