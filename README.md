# limit-order-book
so i'm gonna build a simple limit order book from scratch to demonstrate core market microstructure concepts and data structure tradeoffs 

> this proj prioritises clarity first then performance - intentionally built in stages to demonstrate understanding of tradeoffs in financial market infra

### the goal is to: 
- store buy and sell limit orders
- match orders based on price time priority
- start with naive implementation
- iteratively optimise the data structures

## order structure
limit order book stores buy and sell orders 
- `order_id` - unique identifier
- `side` - buy/sell
- `price` - limit price
- `qty` - quantity
- `timestamp` - implicit arrival ordering (FIFO within price level since I'm using a queue but I'll keep the timestamp for logging) 

<details>
<summary> why no ticker symbol? </summary>

I'm building one order book per symbol which references real world exchanges

If I do optimise it, ticker would be at the routing layer and not inside each order 
</details>

## matching priority 
orders are matched by price-time priority
1. Price priority
  - highest bid matched first
  - lowest ask matched first
2. Time priority
  - earlier orders at same price filled first (using FIFO)

## dsa 

order book maintains: 
```
self.bids: dict[price → deque[Order]]
self.asks: dict[price → deque[Order]]

self.bid_prices: list  # sorted descending
self.ask_prices: list  # sorted ascending

self.order_map: dict[order_id → Order]
```

### hashmap/dictionary 
- O(1) avg lookup by price 
    <details>
    <summary>why avg?</summary>
    due to collisions which may degrade it towards O(n) although most of the time it's O(1)
    </details>
- O(1) insert into price level
- natural grouping by price 

### sorted price list 
- maintain bid and ask prices
- O(1) lookup for best bid and best ask 
- O(n) insertion - could be optimised with heaps

<details>
<summary>heaps</summary>
probs max heap for bid and min heap for ask 

- O(logn) for insert and pop best price as opposed to sorted list O(n)
- the reason why i did not use heap for a start is the deletion on node is not efficient - O(n) to do a full scan 
</details>

### deque
- for price time priority which follows FIFO
  - append new order to the back --> O(1)
  - remove filled orders from front --> O(1)
  - if list was used --> O(n) from pop(0) since it still got to shift all elements to the left 

### secondary index 
`self.order_map: order_id → Order` - points order id to the order 
- fast lookup by ID avg O(1)
- without it cancel would be O(n)
- space for time tradeoff