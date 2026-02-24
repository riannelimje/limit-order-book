from collections import deque
from bisect import insort # to efficiently insert price while maintaining sorted order 
from order import Order, Side
from dll import DoublyLinkedList

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
                book[order.price] = DoublyLinkedList(order.price)

                if is_bid: 
                    # insert negative price for bids to maintain descending order
                    # insort keeps list ascending
                    insort(price_list, -order.price) 
                else:
                    insort(price_list, order.price)
            
            node = book[order.price].append(order)
            self.order_map[order.order_id] = node # links order id to the node in the DLL for easy access 

            print(f"Order {order.order_id} added to book with remaining qty {order.qty}")

    def _match_buy(self, incoming_order):
        # got to check incoming order still has quantity and still have asks avail
        while incoming_order.qty > 0 and self.ask_prices: 
            best_ask_price = self.get_best_ask()

            if incoming_order.price < best_ask_price:
                break # can't match if incoming buy price is less than best ask
            
            price_level = self.asks[best_ask_price]
            best_order_node = price_level.head # get the first node in the price level's DLL

            trade_qty = min(incoming_order.qty, best_order_node.order.qty) # to determine the trade size

            # execute trade
            incoming_order.qty -= trade_qty
            best_order_node.order.qty -= trade_qty

            print(f"Trade executed: {trade_qty} @ {best_ask_price} between {incoming_order.order_id} and {best_order_node.order.order_id}")

            # remove filled resting order 
            if best_order_node.order.qty == 0: 
                price_level.pop_front() # remove from DLL
                del self.order_map[best_order_node.order.order_id] # remove from order map

            # remove empty price level
            if price_level.is_empty():
                del self.asks[best_ask_price]
                self.ask_prices.pop(0) # remove best ask price level

    def _match_sell(self, incoming_order): 
        while incoming_order.qty > 0 and self.bid_prices:
            best_bid_price = self.get_best_bid()

            # Can't match if sell price is higher than best bid
            if incoming_order.price > best_bid_price:
                break

            price_level = self.bids[best_bid_price]
            best_order_node = price_level.head  # first resting order in DLL
            resting_order = best_order_node.order

            # Determine trade size
            trade_qty = min(incoming_order.qty, resting_order.qty)

            # Execute trade
            incoming_order.qty -= trade_qty
            resting_order.qty -= trade_qty

            print(f"Trade executed: {trade_qty} @ {best_bid_price} "
                f"between {incoming_order.order_id} and {resting_order.order_id}")

            # Remove fully filled resting order
            if resting_order.qty == 0:
                price_level.pop_front()
                del self.order_map[resting_order.order_id]

            # Remove empty price level
            if price_level.is_empty():
                del self.bids[best_bid_price]
                self.bid_prices.pop(0)  # still using list, can optimise with SortedDict later

    def cancel_order(self, order_id) -> bool:
        #  lookup in ordermap 
        if order_id not in self.order_map:
            return False
        node = self.order_map[order_id]
        price_level = node.parent
        price_level.remove(node)
        del self.order_map[order_id]

        if price_level.is_empty():
            if node.order.side == Side.BUY:
                del self.bids[price_level.price]
                self.bid_prices.remove(-price_level.price)
            else:
                del self.asks[price_level.price]
                self.ask_prices.remove(price_level.price)
        return True