from order_book import LimitOrderBook
from order import Order, Side
import time

print("\n=== Test 1: No Match ===")

lob = LimitOrderBook()

o1 = Order("1", Side.BUY, 100.0, 10, int(time.time()))
o2 = Order("2", Side.SELL, 105.0, 7, int(time.time()))

lob.add_order(o1)
lob.add_order(o2)

print("Best bid:", lob.get_best_bid())  # expect 100
print("Best ask:", lob.get_best_ask())  # expect 105

print("\n=== Test 2: Full Match ===")

lob = LimitOrderBook()

sell = Order("S1", Side.SELL, 100.0, 5, int(time.time()))
buy = Order("B1", Side.BUY, 105.0, 5, int(time.time()))

lob.add_order(sell)
lob.add_order(buy)

print("Best bid:", lob.get_best_bid())  # expect None
print("Best ask:", lob.get_best_ask())  # expect None

print("\n=== Test 3: Partial Fill (incoming bigger) ===")

lob = LimitOrderBook()

sell = Order("S1", Side.SELL, 100.0, 5, int(time.time()))
buy = Order("B1", Side.BUY, 105.0, 10, int(time.time()))

lob.add_order(sell)
lob.add_order(buy)

print("Best bid:", lob.get_best_bid())  # expect 105
print("Best ask:", lob.get_best_ask())  # expect None

print("\n=== Test 4: Partial Fill (resting bigger) ===")

lob = LimitOrderBook()

sell = Order("S1", Side.SELL, 100.0, 10, int(time.time()))
buy = Order("B1", Side.BUY, 105.0, 4, int(time.time()))

lob.add_order(sell)
lob.add_order(buy)

print("Best bid:", lob.get_best_bid())  # expect None
print("Best ask:", lob.get_best_ask())  # expect 100

print("\n=== Test 5: Multiple Price Levels ===")

lob = LimitOrderBook()

lob.add_order(Order("S1", Side.SELL, 100.0, 5, int(time.time())))
lob.add_order(Order("S2", Side.SELL, 101.0, 5, int(time.time())))
lob.add_order(Order("B1", Side.BUY, 105.0, 6, int(time.time())))

print("Best ask:", lob.get_best_ask())  # expect 101 or None depending on fill

print("\n=== Test 6: FIFO within price level ===")

lob = LimitOrderBook()

lob.add_order(Order("S1", Side.SELL, 100.0, 5, int(time.time())))
lob.add_order(Order("S2", Side.SELL, 100.0, 5, int(time.time())))
lob.add_order(Order("B1", Side.BUY, 105.0, 6, int(time.time())))