from product_service import ProductService

class Sell():
    def __init__(self, id,product_id,date,quantity=0,total_price = 0, product = "",db = None): 
        self.db = db
        product = ProductService(self.db).get_product_by_id(product_id)
        self.id = id
        self.product_id = product_id
        self.date = date
        self.quantity = quantity
        self.total_price = quantity * product.sell_price if product else 0
        self.product = product.product if product else "Unknown Product"

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "date": self.date,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "product": self.product
        }