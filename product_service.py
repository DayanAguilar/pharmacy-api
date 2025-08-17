from product import Product


class ProductService:
    def __init__(self, db):
        self.db = db

    def get_all_products(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        products = []
        for row in rows:
            product_obj = Product(
                product_id=row[0],
                category=row[1],
                product=row[2],
                laboratory=row[3],
                buy_price=row[4],
                sell_price=row[5],
                stock=row[6],
                expire_date=row[7],
                alert_date=row[8]
            )
            products.append(product_obj)
        return products



