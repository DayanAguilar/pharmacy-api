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
                product_id=row[9],
                category=row[0],
                product=row[1],
                laboratory=row[2],
                buy_price=row[3],
                sell_price=row[4],
                stock=row[5],
                expire_date=row[6],
                alert_date=row[7]
            )
            products.append(product_obj)
        return products

    def create_product(self, product):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO products (category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (product.category, product.product, product.laboratory,
             product.buy_price, product.sell_price, product.stock,
             product.expire_date, product.alert_date)
        )
        self.db.commit()
        return cursor.lastrowid

