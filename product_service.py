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
        with self.db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO products (category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (product.category, product.product, product.laboratory,
                 product.buy_price, product.sell_price, product.stock,
                 product.expire_date, product.alert_date)
            )
            self.db.commit()
            return cursor.lastrowid

    def update_product(self, product):
        with self.db.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET category=%s, product=%s, laboratory=%s, buy_price=%s, sell_price=%s, stock=%s, expire_date=%s, alert_date=%s WHERE product_id=%s",
                (product.category, product.product, product.laboratory,
                 product.buy_price, product.sell_price, product.stock,
                 product.expire_date, product.alert_date, product.product_id)
            )
            self.db.commit()
            return cursor.rowcount
    def delete_product(self, product_id):
        with self.db.cursor() as cursor:
            cursor.execute(
                "DELETE FROM products WHERE product_id=%s",
                (product_id,)
            )
            self.db.commit()
            return cursor.rowcount
    
    def get_product_by_id(self, product_id):
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT product_id, category, product, laboratory, buy_price, sell_price, stock, expire_date, alert_date FROM products WHERE product_id=%s",
                (product_id,)
            )
            row = cursor.fetchone()
            if row:
                return Product(
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
        return None
        
    def get_price_by_id(self, product_id):
        product = self.get_product_by_id(product_id)
        return product.sell_price if product else 0
