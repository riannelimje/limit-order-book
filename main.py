from order_book import LimitOrderBook
from order import Order, Side
import time

lob = LimitOrderBook()

o1 = Order("1", Side.BUY, 100.0, 10, int(time.time()))
o2 = Order("2", Side.BUY, 101.0, 5, int(time.time()))
o3 = Order("3", Side.SELL, 105.0, 7, int(time.time()))

lob.add_order(o1)
lob.add_order(o2)
lob.add_order(o3)

print(lob.get_best_bid())  
print(lob.get_best_ask())  