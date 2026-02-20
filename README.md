# limit-order-book
so i'm gonna build a simple limit order book from scratch 

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
probs hashmap, deque, heap or a sorted list 

