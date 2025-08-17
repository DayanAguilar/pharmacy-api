class SellService:
    def __init__(self, db):
        self.db = db

    def create_sell(self, sell_data):
        cursor = self.db.cursor()
        query = """
        INSERT INTO sells (product_id, date)
        VALUES (%s, %s)
        RETURNING id;
        """
        values = (sell_data.product_id, sell_data.date)
        cursor.execute(query, values)
        self.db.commit()
        cursor.close()
        return True
