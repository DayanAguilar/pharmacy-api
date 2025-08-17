class Product:
    def __init__(
        self,
        product_id,
        category="",
        product="",
        laboratory="",
        buy_price=0,
        sell_price=0,
        stock=0,
        expire_date=None,
        alert_date=None,
    ):
        self.category = category
        self.product_id = product_id
        self.product = product
        self.laboratory = laboratory
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.stock = stock
        self.expire_date = expire_date
        self.alert_date = alert_date
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "category": self.category,
            "product": self.product,
            "laboratory": self.laboratory,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "stock": self.stock,
            "expire_date": self.expire_date,
            "alert_date": self.alert_date
        }