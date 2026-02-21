from collections import deque
from bisect import insort # to efficiently insert price while maintaining sorted order 
from order import Order, Side

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
         # see if we can execute any orders immediately
        if order.side == Side.BUY:
            self._match_buy(order)
        else: 
            self._match_sell(order)

        # rest on book if still remaining
        if order.qty > 0:
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

            print(f"Order {order.order_id} added to book with remaining qty {order.qty}")

    def _match_buy(self, incoming_order):
        # got to check incoming order still has quantity and still have asks avail
        while incoming_order.qty > 0 and self.ask_prices: 
            best_ask_price = self.get_best_ask()

            if incoming_order.price < best_ask_price:
                break # can't match if incoming buy price is less than best ask
            
            ask_queue = self.asks[best_ask_price]
            best_ask_order = ask_queue[0]
            trade_qty = min(incoming_order.qty, best_ask_order.qty) # to determine the trade size

            # execute trade
            incoming_order.qty -= trade_qty
            best_ask_order.qty -= trade_qty

            print(f"Trade executed: {trade_qty} @ {best_ask_price} between {incoming_order.order_id} and {best_ask_order.order_id}")

            # remove filled resting order 
            if best_ask_order.qty == 0: 
                ask_queue.popleft() # remove the order from the queue
                del self.order_map[best_ask_order.order_id] # remove from order map

            # remove empty price level
            if not ask_queue:
                del self.asks[best_ask_price]
                self.ask_prices.pop(0) # remove best ask price level

    def _match_sell(self, incoming_order): 
        while incoming_order.qty > 0 and self.bid_prices: 
            best_bid_price = self.get_best_bid()

            if incoming_order.price > best_bid_price: 
                break 

            bid_queue = self.bids[best_bid_price]
            best_bid_order = bid_queue[0]
            trade_qty = min(incoming_order.qty, best_bid_order.qty)
            incoming_order.qty -= trade_qty
            best_bid_order.qty -= trade_qty
            print(f"Trade executed: {trade_qty} @ {best_bid_price} between {incoming_order.order_id} and {best_bid_order.order_id}")

            if best_bid_order.qty == 0:
                bid_queue.popleft()
                del self.order_map[best_bid_order.order_id]

            if not bid_queue:
                del self.bids[best_bid_price]
                self.bid_prices.pop(0)
