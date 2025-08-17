class Sell():
    def __init__(self, id,product_id,date):
        self.id = id
        self.product_id = product_id
        self.date = date

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "date": self.date
        }