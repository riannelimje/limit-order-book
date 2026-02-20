from collections import deque
from bisect import insort # to efficiently insert price while maintaining sorted order 

class LimitOrderBook: 
    def __init__(self):
        self.bids = {}
        self.asks = {}

        # sorted price levels for quick access
        self.bid_prices = [] # descending - cuz we want highest bids
        self.ask_prices = [] # ascending - lowest asks first 

        self.order_map = {}

    def get_best_bid(self):
        if not self.bid_prices:
            return None
        return -self.bid_prices[0]
    
    def get_best_ask(self):
        if not self.ask_prices:
            return None
        return self.ask_prices[0]
    
    def _get_books(self, side):
        # structure - (book, price_list, is_bid)
        if side.name == 'BUY':
            return self.bids, self.bid_prices, True
        return self.asks, self.ask_prices, False
    
    def add_order(self, order):
        book, price_list, is_bid = self._get_books(order.side)

        # create price level if new
        if order.price not in book:
            book[order.price] = deque()

            if is_bid: 
                # insert negative price for bids to maintain descending order
                # insort keeps list ascending
                insort(price_list, -order.price) 
            else:
                insort(price_list, order.price)
        
        book[order.price].append(order)
        self.order_map[order.order_id] = order # links order id to the order obj for easy access 
        
