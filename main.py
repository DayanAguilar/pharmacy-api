import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime

from product_service import ProductService
from product import Product
from sell_service import SellService
from sell import Sell
from pydantic_models import ProductIn, ProductOut, SellIn, SellOut

load_dotenv()
POSTGRESS_SQL_URL = os.environ["POSTGRESS_SQL_URL"]

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,  
    maxconn=10, 
    dsn=POSTGRESS_SQL_URL
)

if not connection_pool:
    raise Exception("Error creando el pool de conexiones")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


@app.get("/products")
def get_products(conn=Depends(get_conn)):
    try:
        product_service = ProductService(conn)
        products = product_service.get_all_products()
        return [p.to_dict() for p in products]
    except Exception as e:
        return JSONResponse(status_code=404, content={"error": str(e)})


@app.post("/products", response_model=ProductOut)
def create_product(product: ProductIn, conn=Depends(get_conn)):
    try:
        product_service = ProductService(conn)
        product_obj = Product(
            product_id=None,
            category=product.category,
            product=product.product,
            laboratory=product.laboratory,
            buy_price=product.buy_price,
            sell_price=product.sell_price,
            stock=product.stock,
            expire_date=product.expire_date,
            alert_date=product.alert_date,
        )
        product_id = product_service.create_product(product_obj)
        product_obj.product_id = product_id
        return product_obj.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductIn, conn=Depends(get_conn)):
    try:
        product_service = ProductService(conn)
        existing_product = product_service.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        existing_product.category = product.category
        existing_product.product = product.product
        existing_product.laboratory = product.laboratory
        existing_product.buy_price = product.buy_price
        existing_product.sell_price = product.sell_price
        existing_product.stock = product.stock
        existing_product.expire_date = product.expire_date
        existing_product.alert_date = product.alert_date
        rows_updated = product_service.update_product(existing_product)
        if rows_updated == 0:
            raise HTTPException(status_code=400, detail="Update failed")
        return existing_product.to_dict()
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/products/{product_id}")
def delete_product(product_id: int, conn=Depends(get_conn)):
    try:
        product_service = ProductService(conn)
        rows_deleted = product_service.delete_product(product_id)
        if rows_deleted == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/sells", response_model=SellOut)
def create_sell(sell: SellIn, conn=Depends(get_conn)):
    try:
        product_service = ProductService(conn)
        sell_service = SellService(conn)

        product = product_service.get_product_by_id(sell.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        total_price = sell.quantity * product.sell_price
        sell_date = datetime.datetime.now().date()
        sell_obj = SellOut(
            id=None,
            product_id=sell.product_id,
            date=sell_date,
            quantity=sell.quantity,
            total_price=total_price,
            product=product.product
        )
        sell_id = sell_service.create_sell(sell_obj)
        sell_obj.sell_id = sell_id

        return sell_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/sells/{date}")
def get_sells_by_date(date: str, conn=Depends(get_conn)):
    try:
        sell_service = SellService(conn)
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        sells = sell_service.generate_sell_report_by_date(date_obj)
        if sells is None:
            sells = []
        return sells
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
