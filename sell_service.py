from sell import Sell
from product_service import ProductService


class SellService:
    def __init__(self, db):
        self.db = db

    def create_sell(self, sell_data):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT stock FROM products WHERE product_id = %s",
                (sell_data.product_id,),
            )
            result = cursor.fetchone()
            if not result:
                raise Exception("Product not found")
            current_stock = result[0]
            if sell_data.quantity > current_stock:
                raise Exception(
                    f"Not enough stock. Available: {current_stock}, Requested: {sell_data.quantity}"
                )
            query = """
            INSERT INTO sells (product_id, date, quantity, total_price, product)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            values = (
                sell_data.product_id,
                sell_data.date,
                sell_data.quantity,
                sell_data.total_price,
                sell_data.product,
            )
            cursor.execute(query, values)
            sell_id = cursor.fetchone()[0]
            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                (sell_data.quantity, sell_data.product_id),
            )
            self.db.commit()
            return sell_id

        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            cursor.close()

    def report_by_date(self, date):
        cursor = self.db.cursor()
        query = "SELECT * FROM sells WHERE date = %s "
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        sells = []
        for row in rows:
            sell_obj = Sell(
                id=row[0],
                product_id=row[1],
                date=row[2],
                quantity=row[3],
                total_price=row[4] if row[4] is not None else 0,
                product=row[5] if row[5] is not None else "",
                db=self.db,
            )
            sells.append(sell_obj)
        cursor.close()
        return sells

    def generate_sell_report_by_date(self, date):
        sells = self.report_by_date(date)
        report = []
        for s in sells:
            product_service = ProductService(self.db)
            product = product_service.get_product_by_id(s.product_id)
            if product:
                report.append({"product_name": product.product, "date": s.date})
                print(f"Sell ID: {s.id}, Product: {product.product}, Date: {s.date}")
            else:
                print(f"Sell ID: {s.id}, Product ID: {s.product_id} not found.")
