from product_service import ProductService
from product import Product
from sell_service import SellService
from sell import Sell
import psycopg2
from dotenv import load_dotenv
import os
import datetime
load_dotenv()
POSTGRESS_SQL_URL = os.environ["POSTGRESS_SQL_URL"]

conn = psycopg2.connect(POSTGRESS_SQL_URL)
product_service = ProductService(conn)
products = product_service.get_all_products()

product = Product(
    product_id=1033,
    category="ejemplo",
    product="Paracetamol",
    laboratory="Bayer",
    buy_price=5.0,
    sell_price=7.5,
    stock=100,
    expire_date="2024-12-31",
    alert_date="2024-11-30"
)

sell = Sell(
    id=None,
    product_id=1033,
    date=datetime.datetime.now().strftime("%Y-%m-%d"),
)
sell_service = SellService(conn)
print(sell_service.create_sell(sell))
# # print(product_service.delete_product(1033))
# for p in products:
#     print(p.to_dict())

# product = product_service.get_product_by_id(1032)
# if product:
#     print(product.to_dict())

