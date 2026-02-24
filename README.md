# limit-order-book
so i'm gonna build a simple limit order book from scratch to demonstrate core market microstructure concepts and data structure tradeoffs 

> this proj prioritises clarity first then performance - intentionally built in stages to demonstrate understanding of tradeoffs in financial market infra

### the goal is to: 
- store buy and sell limit orders
- match orders based on price time priority
- start with naive implementation
- iteratively optimise the data structures

## optimisation roadmap


| version  | price structure         | queue structure | insert   | cancel | best price             | notes                                                                                    |
| -------- | ----------------------- | --------------- | -------- | ------ | ---------------------- | ---------------------------------------------------------------------------------------- |
| v1       | sorted list + bisect    | deque           | O(n)     | O(k)   | O(1)                   | naive queues, cancel scans deep queues linearly (k = depth at price level)               |
| v2 (now) | sorted list + bisect    | DLL             | O(n)     | O(1)   | O(1)                   | replace deque with doubly-linked list → cancellation becomes O(1) while maintaining FIFO |
| v3       | SortedDict              | DLL             | O(log n) | O(1)   | O(1)                   | handle very large price universes → insertion no longer O(n) due to shifting             |
| v4       | BTreeMap / Rust/C++ map | DLL             | O(log n) | O(1)   | O(1) + cache efficient | high-performance, low-level memory optimisations                                         |

>initially thought deque was fine but the performance benchmarks caught the degredation so that pain point is managed first!

heap was considered but rejected - arbitrary deletion is O(n) which breaks cancellation performance

lazy deletion workaround exists but silently degrades best price lookup under heavy cancellations

<details>
<summary>further explaination - why not heap + lazy deletion?</summary>
again, removing a cancelled order with heaps requires O(n) scan 

lazy deletion
- don't actually remove the cancelled order from the heap
- just marks it as cancelled
- when popping from the heap, it skips marked entries 

**main problem** 

a busy market with lots of cancellations slowly fills the heap with stale garbage
- this means O(1) best price lookup silently degrades as every lookup has to skip through dead entries before finding a live one!

example: 
```
heap = [cancelled, cancelled, cancelled, 101, 102]
# we have to dig through the trash to reach 101
```

this is why heap was rejected - it trades one problem (slow deletion) for another (dishonest lookup)
best price lookup is technically O(1) in the best case but **degrades proportionally** to cancellation volume 
```
mechanics - pop, check, if cancelled, pop again else it's the best one!
clean heap - O(1) --> pop
1 stale entry - O(1) --> skip 1 time 
10 stale - O(10) --> skip 10 times
1000 stale - O(1000) --> basically you pop until you get the correct one 
```
sorted list is slower on insert but at least its complexity is predictable

lazy deletions good when 
- deletions are infrequent relative to reads
- only ever need the single best element 
- have a natural cleanup moment 

and i don't think the order book passes any of these(?) 
- cancellations are frequent
- we need arbitrary price level access to reach to any level and not just the top element 
- unless we implement one ourselves 
  - mostly got to heapify which is O(n)
  - when to trigger it is an issue - has to be not too frequent and not too infrequent 
  - cleanup would cost time and real exchange don't wait 

general principle 
> a workaround that requires you to build more infra to manage the workaround is a sign that you chose the wrong data structure for the problem
</details>

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

<details>
<summary> cancel rules </summary>
given an order id: 

1. find the order fast - via `order_map` --> O(1) avg 
2. locate its correct price level queue
3. remove it from deque - O(k), k is orders at that price 
4. clean up empty price levels - O(1)
5. remove from order_map

why O(k)? 
- although price lookup is constant time, removing from the middle of deque requires a linear scan to locate the order within that price level 

this implementation (v1) demonstrates the baseline behaviour

<details>
<summary> pros and cons of current implementation </summary>

**pros**
- simple implementation
- memory efficient

**cons**
- cancel cost grows with queue depth 
- not optimal for very deep prices 
- potential hotspot under heavy cancel flow

</details>

future optimisations 
- doubly linked list per price level
- direct node pointers stored in order map 
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
  - cancel order --> O(k), k = depth of queue
    - it will be slow with a large queue - probs use DLL 

### secondary index 
`self.order_map: order_id → Order` - points order id to the order 
- fast lookup by ID avg O(1)
- without it cancel would be O(n)
- space for time tradeoff

### doubly linked list 
- replaces deque for each price level to improve cancellation performance 
  - see performance benchmark 
- maintains FIFO for price time priority 
  - append new order to tail - O(1)
  - remove filled order from head - O(1)
  - cancel any order in the middle - O(1)
    - direct pointer via order_map
- fast cancellation under deep queues

```
Price 100 DLL: head -> [O1] <-> [O2] <-> [O3] <- tail
Order_map: { "O1": node1, "O2": node2, "O3": node3 }

Cancel O2:
  node2.prev.next = node2.next
  node2.next.prev = node2.prev
Result: head -> [O1] <-> [O3] <- tail
```

## complexity summary

| operation | time | why |
|---|---|---|
| add order | O(n) | bisect finds position O(log n) but list shifts O(n) |
| match order | O(k) | k = number of price levels consumed |
| cancel order | O(n) | order_map O(1) lookup, list removal O(n) |
| best bid/ask | O(1) | first element of sorted list |
| v2 target | O(log n) | SortedDict replaces sorted list |

## testing

the engine is validated with pytest covering:

- non-crossing orders
- full fills
- partial fills
- multi-level sweeps
- FIFO within price level
- order_map consistency
- empty book edge cases

tests were written before optimisation to ensure refactors preserve correctness.

## performance benchmarks 
benchmarks were run on python 3.13

**table (v1)** - see `benchmark_results.csv` for more

| Operation | Orders | Time (s) | Throughput (ops/sec) |
|------------|---------|-----------|------------------------|
| Inserts (passive) | 100,000 | 0.4787 | 208,905 |
| Cancel (deep queue) | 50,000 | 4.9983 | 10,003 |
| Matching (aggressive) | 50,000 | 0.2860 | 174,800 |

### observations
- cancellation throughput drops significantly under deep price levels
  - expected outcome since `deque.remove` requires linear traversal within price level
  - doubly linked list would help to achieve O(1) cancellation by storing a direct node pointer 

### roadmap 
i think i'll implement a dll first followed by SortedDict

<details>
<summary>why not SortedDict first?</summary>
although sorted lists have O(n) insertion due to shifting theoretically, current benchmarks shows insertion throughput to be relatively high 

the primary bottleneck now is the cancellation under deep price levels so i'll work on optimising that first!
</details>

<details>
<summary>v2 plan</summary>

- replace deque with dll at each price level --> O(1) append and removal
- update order to store a reference to its node 
- update add order and match methods 
- keep sorted price list for now with the bisect.insory - stil O(1)
- update cancel logic
</details>

### benchmarks - DLL optimisation (v2)

| Operation | v1 (ops/sec) | v2 (ops/sec) | Comment |
|-----------|--------------|--------------|---------|
| Inserts 100k | 208,905 | 68,730 | DLL insertion slightly slower due to node allocations. |
| Cancel 50k | 10,003 | 2,541,812 | Massive speedup! O(1) removal using order_map + DLL nodes. |
| Matching 50k | 174,799 | 72,668 | Slightly slower, but FIFO preserved. |

**takeaways:**
1. cancellations were the main bottleneck — solved by DLL + node references.
2. inserts and matching remain acceptable; minor overhead from DLL.
3. next step: replace sorted price lists with `SortedDict` for O(log n) price-level maintenance.

to verify that SortedDict is needed, i added an additional benchmark to test many price levels and scaled it with 10,000, 50,000 and 100,000 price levels (every order creates a new price level!)

| Orders (n) | Elapsed Time (s) | Throughput (ops/sec) | Relative Slowdown |
| ---------- | ---------------- | -------------------- | ----------------- |
| 10,000     | 0.145            | 68,924               | 1.0× (baseline)   |
| 50,000     | 1.019            | 49,051               | 7.0×              |
| 100,000    | 3.612            | 27,686               | 24.9×             |

> demonstrates that list based price maintenance does not scale under heavy price fragmentation

<details>
<summary>why lists become slow?</summary> 
although bisect.insort takes O(logn) to find element

when we insert a new element in front, every element shifts to the right 

```
ls = [100,101]
# when we add 99
ls = [99,100,101]
```

so insertion is O(n)

when we insert 100,000 distinct prices, each insertion costs O(n) so total work becomes O(n^2) - following AP - (1 + 2 + 3 + ... + n) where sum = n/2(1+n)
</details>
