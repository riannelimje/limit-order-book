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
        return self.bid_prices[0]
    
    def get_best_ask(self):
        if not self.ask_prices:
            return None
        return self.ask_prices[0]