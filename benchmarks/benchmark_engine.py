import csv
import time
import random
from order_book import LimitOrderBook
from order import Order, Side
from datetime import datetime, timezone
from pathlib import Path

RESULTS_FILE = Path("benchmark_results.csv")
VERSION = "v2"

def save_result(benchmark_type, n, elapsed):
    ops = n / elapsed

    file_exists = RESULTS_FILE.exists()

    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        # write header once
        if not file_exists:
            writer.writerow([
                "timestamp",
                "benchmark_type",
                "n_orders",
                "elapsed_sec",
                "ops_per_sec",
                "version",
            ])

        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            benchmark_type,
            n,
            f"{elapsed:.6f}",
            f"{ops:.2f}",
            VERSION,
        ])

def benchmark_inserts(n=100_000):
    # how fast can the book accept passive orders? 
    book = LimitOrderBook()
    start = time.perf_counter() # this is a high precision timer, standard for benchmarking

    # populate book
    for i in range(n): 
        price = random.randint(95, 105) # random price between 95 and 105
        order = Order(
            order_id=str(i), 
            side=Side.BUY, 
            price=price, 
            qty=random.randint(1, 10), 
            timestamp=i
        )
        book.add_order(order)

    end = time.perf_counter()

    print(f"Inserted {n} orders in {end - start:.4f} seconds")
    print(f"ops/sec: {n / (end - start):,.2f}") # calculate throughput - how many order per second can the engine handle? 

    save_result("inserts", n, end - start)

def benchmark_cancel(n=50_000):
    # cancel stress test: add n orders, then cancel them all
    book = LimitOrderBook()
    order_ids = []

    for i in range(n): 
        order = Order(
            order_id=str(i), 
            side=Side.BUY, 
            price=100, # same price to simulate a deep queue
            qty=1, 
            timestamp=i
        )
        book.add_order(order)
        order_ids.append(str(i))

    # shuffle cancels to simulate random cancellations
    random.shuffle(order_ids)
    start = time.perf_counter()

    for order_id in order_ids:
        book.cancel_order(order_id)

    end = time.perf_counter()

    print(f"Cancelled {n} orders in {end - start:.4f} seconds")
    print(f"ops/sec: {n / (end - start):,.2f}")

    save_result("cancel", n, end - start)

def benchmark_matching(n=50_000):
    # matching stress test: add n buy orders, then n sell orders that match them
    book = LimitOrderBook()

    # load resting sells 
    for i in range(n): 
        book.add_order(Order(
            order_id=f"S{i}", 
            side=Side.SELL, 
            price=100, 
            qty=1, 
            timestamp=i
        ))

    start = time.perf_counter()

    # aggressive buys 
    for i in range(n, 2*n):
        book.add_order(Order(
            order_id=f"B{i}", 
            side=Side.BUY, 
            price=105, 
            qty=1, 
            timestamp=i
        ))

    end = time.perf_counter()

    print(f"Matched {n} orders in {end - start:.4f} seconds")
    print(f"ops/sec: {n / (end - start):,.2f}")

    save_result("matching", n, end - start)

def benchmark_many_price_levels(n=100_000):
    """
    Stress test: many distinct price levels.
    """
    book = LimitOrderBook()

    start = time.perf_counter()

    for i in range(n):
        price = 100 + i  # EVERY order at a new price level
        order = Order(
            order_id=str(i),
            side=Side.BUY,
            price=price,
            qty=1,
            timestamp=i
        )
        book.add_order(order)

    end = time.perf_counter()

    return { 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_type": "many_price_levels",
        "n_orders": n,
        "elapsed_sec": end - start,
        "ops_per_sec": n / (end - start),
    }

def run_scaling_tests():
    sizes = [10_000, 50_000, 100_000]
    results = []

    for n in sizes:
        print(f"Running many_price_levels for {n} orders...")
        result = benchmark_many_price_levels(n)
        results.append(result)
        print(result)
        save_result(result["benchmark_type"], n, result["elapsed_sec"])

if __name__ == "__main__":
    random.seed(42) # for reproducibility
    print("=== Benchmark: Inserts ===")
    benchmark_inserts()
    print("\n=== Benchmark: Cancellations ===")
    benchmark_cancel()
    print("\n=== Benchmark: Matching ===")
    benchmark_matching()
    print("\n=== Benchmark: Many Price Levels (scaling test) ===")
    run_scaling_tests()