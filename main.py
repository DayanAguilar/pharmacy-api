import psycopg2
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime
import logging
import sys

from product_service import ProductService
from product import Product
from sell_service import SellService
from sell import Sell
from pydantic_models import ProductIn, ProductOut, SellIn, SellOut

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
POSTGRESS_SQL_URL = os.environ["POSTGRESS_SQL_URL"]

global_connection = None

def init_connection():
    global global_connection
    try:
        global_connection = psycopg2.connect(
            dsn=POSTGRESS_SQL_URL,
            application_name="pharmacy_api_single_conn"
        )
        global_connection.autocommit = False
        logger.info("✅ Database connection established successfully")
        return global_connection
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        raise Exception(f"Error conectando a la base de datos: {e}")

def get_connection():
    global global_connection
    try:
        if global_connection is None or global_connection.closed:
            logger.info("Reconnecting to database...")
            init_connection()
        else:
            try:
                with global_connection.cursor() as test_cursor:
                    test_cursor.execute("SELECT 1")
            except:
                logger.info("Connection lost, reconnecting...")
                init_connection()
        
        return global_connection
    except Exception as e:
        logger.error(f"Error getting connection: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

init_connection()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    """Dependency que retorna la conexión global"""
    conn = get_connection()
    return conn

@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})

@app.get("/products")
def get_products(conn=Depends(get_conn)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
            try:
                product_service = ProductService(conn)
                products = product_service.get_all_products()
                cursor.execute("COMMIT")
                return [p.to_dict() for p in products]
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return JSONResponse(status_code=404, content={"error": str(e)})

@app.post("/products", response_model=ProductOut)
def create_product(product: ProductIn, conn=Depends(get_conn)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
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
                
                cursor.execute("COMMIT")
                logger.info(f"Product created with ID: {product_id}")
                return product_obj.to_dict()
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductIn, conn=Depends(get_conn)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
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
                
                cursor.execute("COMMIT")
                logger.info(f"Product {product_id} updated successfully")
                return existing_product.to_dict()
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/products/{product_id}")
def delete_product(product_id: int, conn=Depends(get_conn)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
            try:
                product_service = ProductService(conn)
                rows_deleted = product_service.delete_product(product_id)
                if rows_deleted == 0:
                    raise HTTPException(status_code=404, detail="Product not found")
                
                cursor.execute("COMMIT")
                logger.info(f"Product {product_id} deleted successfully")
                return {"message": "Product deleted successfully"}
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sells", response_model=SellOut)
def create_sell(sell: SellIn, conn=Depends(get_conn)):
    logger.info(f"Creating sell for product_id: {sell.product_id}, quantity: {sell.quantity}")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
            try:
                product_service = ProductService(conn)
                sell_service = SellService(conn)

                product = product_service.get_product_by_id(sell.product_id)
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")

                if product.stock < sell.quantity:
                    raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.stock}, Requested: {sell.quantity}")

                total_price = sell.quantity * product.sell_price
                sell_date = datetime.datetime.now().date()

                sell_obj = Sell(
                    id=None,
                    product_id=sell.product_id,
                    date=sell_date,
                    quantity=sell.quantity,
                    total_price=total_price,
                    db = conn,
                )
                sell_id = sell_service.create_sell(sell_obj)

                new_stock = product.stock - sell.quantity
                product.stock = new_stock
                rows_updated = product_service.update_product(product)
                
                if rows_updated == 0:
                    raise Exception("Failed to update product stock")

                cursor.execute("COMMIT")
                
                logger.info(f"Sell created successfully. Sell ID: {sell_id}, New stock: {new_stock}")

                sell_response = SellOut(
                    sell_id=sell_id,
                    product_id=sell.product_id,
                    date=sell_date,
                    quantity=sell.quantity,
                    total_price=total_price,
                    product=product.product
                )
                
                return sell_response
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
                
    except HTTPException as he:
        logger.error(f"HTTP Error creating sell: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error creating sell: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/sells/{date}")
def get_sells_by_date(date: str, conn=Depends(get_conn)):
    try:
        with conn.cursor() as cursor:
            cursor.execute("BEGIN")
            try:
                sell_service = SellService(conn)
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                sells = sell_service.generate_sell_report_by_date(date_obj)
                cursor.execute("COMMIT")
                if sells is None:
                    sells = []
                return sells
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        logger.error(f"Error getting sells by date: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    global global_connection
    if global_connection and not global_connection.closed:
        global_connection.close()
        logger.info("Database connection closed")