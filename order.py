from enum import Enum

class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class Order:
    def __init__(self, order_id: str, side: Side, price: float, qty: int, timestamp: int):
        self.order_id = order_id
        self.side = side
        self.price = price
        self.qty = qty
        self.timestamp = timestamp

    def __repr__(self):
        return f"Order(order_id={self.order_id}, side={self.side.value}, price={self.price}, qty={self.qty}, timestamp={self.timestamp})"