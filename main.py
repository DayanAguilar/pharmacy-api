from product_service import ProductService
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
POSTGRESS_SQL_URL = os.environ["POSTGRESS_SQL_URL"]

conn = psycopg2.connect(POSTGRESS_SQL_URL)
product_service = ProductService(conn)
products = product_service.get_all_products()

for product in products:
    print(product.to_dict())