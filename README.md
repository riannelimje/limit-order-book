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

<details>
<summary> matching rules </summary>

- buy price >= best ask (lowest ask)
- sell price <= besk bid (highest bid)
- within price level (`popleft()` - following FIFO)
</details>

<details>
<summary> aggressor vs resting order semantics </summary>
incoming orders are always matched before being admitted to the book - ensures correct aggressor/passive behaviour similar to real exchanges 

resting order - order that is already sitting in the book waiting to be matched

execution rule: 
- trade occurs at the resting order's price 
- incoming order == aggressor 
- order on the book == resting order / passive
</details>

<details>
<summary> matching engine flow </summary>
when a new order arrives: 

1. match against opposite book 
2. execute trades using price time priority 
3. reduce qty on both sides 
4. remove fully fille resting orders
5. if incoming still has qty --> rest on book 
</details>

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

<details>
<summary>sorted price insertion strategy </summary>

to maintain sorted price levels efficiently, I use binary search insertion via `bisect.insort`
- ask prices - maintained in ascending order
- bid prices - maintained in descending order 

python's bisect only supports ascending order so i store the price using a descending trick 
- ask --> `insort(price_list, order.price)`
- bid --> insert negative price into ascending list `insort(price_list, -order.price)`

this keeps lookup best price at O(1), insertion at O(n) due to shifting and search position at O(logn)

**example:**
```
ask_prices = [101, 102, 103]   # ascending, best ask = ask_prices[0]
bid_prices = [-101, -99] # stored negative, best bid = -bid_prices[0]

# to get real best bid:
best_bid = -bid_prices[0]  # 101
```

so inserting a new bid at $100:
```
before: [-101, -99]
insert: -100
after:  [-101, -100, -99]  # correct descending order preserved
```
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

## complexity summary

| operation | time | why |
|---|---|---|
| add order | O(n) | bisect finds position O(log n) but list shifts O(n) |
| match order | O(k) | k = number of price levels consumed |
| cancel order | O(n) | order_map O(1) lookup, list removal O(n) |
| best bid/ask | O(1) | first element of sorted list |
| v2 target | O(log n) | SortedDict replaces sorted list |

## optimisation roadmap

| version | price structure | insert | delete | best price |
|---|---|---|---|---|
| v1 (now) | sorted list + bisect | O(n) | O(n) | O(1) |
| v2 | SortedDict | O(log n) | O(log n) | O(1) |
| v3 | BTreeMap (Rust/C++) | O(log n) | O(log n) | O(1) + cache efficient |

heap was considered but rejected - arbitrary deletion is O(n) which breaks cancellation performance. lazy deletion workaround exists but silently degrades best price lookup under heavy cancellations.